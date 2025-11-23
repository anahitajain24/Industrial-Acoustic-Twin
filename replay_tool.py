import sys
import os
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import (QApplication, QFileDialog, QWidget, QVBoxLayout, 
                             QPushButton, QMessageBox, QLabel)
from PyQt5.QtCore import Qt
from scipy.io import wavfile

CHUNK_SIZE = 2048

class ReplayTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Forensics Replay Station")
        self.resize(1000, 750)
        
        # 1. SETUP LAYOUT (Graph on top, Button on bottom)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # 2. FILE PICKER
        self.filename, _ = QFileDialog.getOpenFileName(None, "Select Crash Log", "./logs", "WAV Files (*.wav)")
        
        if not self.filename:
            sys.exit() # User cancelled
            
        self.setWindowTitle(f"REPLAYING: {os.path.basename(self.filename)}")
        
        # Load Data
        self.rate, self.data = wavfile.read(self.filename)
        self.ptr = 0
        
        # 3. GRAPHICS WIDGET (The Charts)
        self.graph_layout = pg.GraphicsLayoutWidget()
        self.layout.addWidget(self.graph_layout)
        
        # Plot 1: Waveform
        self.plot_wave = self.graph_layout.addPlot(title="<span style='color: #00FF00'>Recorded Waveform</span>")
        self.plot_wave.setYRange(-1, 1)
        self.plot_wave.showGrid(x=True, y=True, alpha=0.3)
        self.curve_wave = self.plot_wave.plot(pen=pg.mkPen('#00FF00', width=1))
        
        self.graph_layout.nextRow()
        
        # Plot 2: FFT
        self.plot_fft = self.graph_layout.addPlot(title="<span style='color: #FFA500'>Frequency Spectrum</span>")
        self.plot_fft.setRange(xRange=(0, 4000), yRange=(0, 50))
        self.plot_fft.showGrid(x=True, y=True, alpha=0.3)
        self.curve_fft = self.plot_fft.plot(pen=pg.mkPen('#FFA500', width=2), fillLevel=0, brush=(255, 165, 0, 50))

        # 4. DELETE BUTTON (The New Feature)
        self.btn_delete = QPushButton("🗑 DELETE THIS LOG (FALSE ALARM)")
        self.btn_delete.setStyleSheet("""
            background-color: #550000; 
            color: white; 
            font-weight: bold; 
            padding: 15px;
            font-size: 14px;
            border: 1px solid #FF0000;
        """)
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_log)
        self.layout.addWidget(self.btn_delete)
        
        # 5. PLAYBACK TIMER
        interval = (CHUNK_SIZE / self.rate) * 1000
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(int(interval))

    def update_plots(self):
        # Loop Logic
        if self.ptr + CHUNK_SIZE > len(self.data):
            self.ptr = 0 
            
        chunk = self.data[self.ptr : self.ptr + CHUNK_SIZE]
        self.ptr += CHUNK_SIZE
        
        # Math
        window = np.hanning(len(chunk))
        fft_data = (np.abs(np.fft.rfft(chunk * window)) / CHUNK_SIZE) * 200
        freqs = np.fft.rfftfreq(CHUNK_SIZE, 1/self.rate)
        
        self.curve_wave.setData(chunk)
        self.curve_fft.setData(freqs, fft_data)

    def delete_log(self):
        # 1. PAUSE
        self.timer.stop()
        
        # 2. CONFIRMATION DIALOG
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Are you sure you want to delete this file?")
        msg.setInformativeText("This action cannot be undone.")
        msg.setWindowTitle("Confirm Deletion")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        # Style the popup to match dark theme
        msg.setStyleSheet("QLabel{color: white;} QPushButton{width: 60px;}")
        
        retval = msg.exec_()
        
        if retval == QMessageBox.Yes:
            # 3. DELETE ACTION
            try:
                os.remove(self.filename)
                print(f"Deleted: {self.filename}")
                self.close() # Close window after delete
            except Exception as e:
                print(f"Error deleting file: {e}")
        else:
            # Resume if they clicked No
            self.timer.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Global Dark Theme for the Container
    app.setStyleSheet("QWidget { background-color: #222; color: #DDD; }")
    pg.setConfigOption('background', 'k')
    win = ReplayTool()
    win.show()
    sys.exit(app.exec_())