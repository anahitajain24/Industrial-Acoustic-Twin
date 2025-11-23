import sys
import os
import time
import datetime
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication
import sounddevice as sd
from scipy.io import wavfile

# --- CONFIGURATION ---
SAMPLE_RATE = 44100   # Hz (Standard Audio)
CHUNK_SIZE = 2048     # FFT Resolution
LOG_DURATION = 5      # Seconds of pre-trigger history to save
BUFFER_SIZE = SAMPLE_RATE * LOG_DURATION 

# --- ALARM SETTINGS ---
FAULT_FREQ_LOW = 2000   # Whistle Start (Hz)
FAULT_FREQ_HIGH = 3000  # Whistle End (Hz)
FAULT_THRESHOLD = 20    # Sensitivity (0-50 scale)

class LiveMonitor(pg.GraphicsLayoutWidget):
    def __init__(self):
        super().__init__(show=True, title="Live Condition Monitor")
        self.resize(1000, 700)
        self.setWindowTitle("Live Condition Monitor (DAQ)")
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        # Data & State
        self.audio_buffer = np.zeros(BUFFER_SIZE)
        self.last_save_time = 0
        self.cooldown = 5  # Seconds between saves

        # --- PLOT 1: TIME DOMAIN (Oscilloscope) ---
        self.plot_wave = self.addPlot(title="<span style='color: #00FF00'>Raw Waveform (Time)</span>")
        self.plot_wave.setYRange(-1, 1)
        self.plot_wave.showGrid(x=True, y=True, alpha=0.3)
        self.curve_wave = self.plot_wave.plot(pen=pg.mkPen('#00FF00', width=1))
        
        self.nextRow()
        
        # --- PLOT 2: FREQUENCY DOMAIN (Spectrum Analyzer) ---
        self.plot_fft = self.addPlot(title="<span style='color: #FFA500'>Frequency Spectrum (FFT)</span>")
        self.plot_fft.setRange(xRange=(0, 4000), yRange=(0, 50))
        self.plot_fft.showGrid(x=True, y=True, alpha=0.3)
        self.curve_fft = self.plot_fft.plot(pen=pg.mkPen('#FFA500', width=2), fillLevel=0, brush=(255, 165, 0, 50))
        
        # Visual: The "Danger Zone" Box
        self.idx_min = int(FAULT_FREQ_LOW * CHUNK_SIZE / SAMPLE_RATE)
        self.idx_max = int(FAULT_FREQ_HIGH * CHUNK_SIZE / SAMPLE_RATE)
        dz = pg.LinearRegionItem([FAULT_FREQ_LOW, FAULT_FREQ_HIGH], brush=(255,0,0,30), movable=False)
        self.plot_fft.addItem(dz)

        # --- START DAQ (Microphone) ---
        try:
            self.stream = sd.InputStream(channels=1, samplerate=SAMPLE_RATE, callback=self.callback)
            self.stream.start()
            print("System Active. Monitoring for faults...")
        except Exception as e:
            print(f"Mic Error: {e}")

        # Update Loop (30 FPS)
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(30)

    def callback(self, indata, frames, time, status):
        """High-speed background thread for data capture"""
        self.audio_buffer = np.roll(self.audio_buffer, -frames)
        self.audio_buffer[-frames:] = indata[:, 0]

    def update(self):
        """Main UI thread for Math and Visualization"""
        # Get latest chunk
        recent = self.audio_buffer[-CHUNK_SIZE:]
        
        # 1. Hanning Window (Fixes Spectral Leakage)
        window = np.hanning(len(recent))
        
        # 2. FFT Calculation (with 200x Gain for visibility)
        fft_data = (np.abs(np.fft.rfft(recent * window)) / CHUNK_SIZE) * 400
        freqs = np.fft.rfftfreq(CHUNK_SIZE, 1/SAMPLE_RATE)
        
        # 3. ALARM LOGIC
        # Check max value inside the Danger Zone indices
        max_val = np.max(fft_data[self.idx_min:self.idx_max]) if self.idx_max > self.idx_min else 0
        
        if max_val > FAULT_THRESHOLD:
            # TRIGGER STATE
            self.plot_fft.setTitle("<span style='color:red; font-weight:bold; font-size:16pt'>⚠ CRITICAL FAULT - LOGGING DATA ⚠</span>")
            self.curve_fft.setPen(pg.mkPen('r', width=3))
            self.curve_fft.setBrush((255, 0, 0, 100))
            
            # Save "Black Box" Data (with debounce)
            if time.time() - self.last_save_time > self.cooldown:
                self.save_data()
                self.last_save_time = time.time()
        else:
            # NORMAL STATE
            self.plot_fft.setTitle("<span style='color:#FFA500'>Frequency Spectrum (FFT)</span>")
            self.curve_fft.setPen(pg.mkPen('#FFA500', width=2))
            self.curve_fft.setBrush((255, 165, 0, 50))

        # Update Plots (Downsample wave by 50 to improve FPS)
        self.curve_wave.setData(self.audio_buffer[::50])
        self.curve_fft.setData(freqs, fft_data)

    def save_data(self):
        """Dumps the circular buffer to a WAV file"""
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = os.path.join("logs", f"CRITICAL_EVENT_{ts}.wav")
        # Save the full buffer (history)
        wavfile.write(fname, SAMPLE_RATE, self.audio_buffer.astype(np.float32))
        print(f"⚠ EVENT CAPTURED: {fname}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pg.setConfigOption('background', 'k')
    win = LiveMonitor()

    sys.exit(app.exec_())
