# Industrial Acoustic Twin (Condition Monitoring System)

### 🔴 Live Monitoring | 📊 FFT Analysis | 🚨 Auto-Logging

A Python-based Digital Twin that simulates an industrial vibration analysis system. It detects mechanical fault signatures (simulated via frequency anomalies) and triggers automated "Black Box" data logging, mimicking Flight Data Recorder (FDR) functionality.

*(Above: System detecting a high-frequency fault and triggering the Red Alarm state)*

## 🛠 Tech Stack
* Language: Python 3.10+
* DAQ: `sounddevice` (44.1kHz real-time sampling)
* Signal Processing: `NumPy` & `SciPy` (FFT, Hanning Window, Circular Buffering)
* Visualization: `PyQtGraph` (High-performance real-time plotting)
* GUI: `PyQt5`

## 🚀 Features
1. Real-Time DAQ: Captures audio at 44.1kHz and processes chunks of 2048 samples.
2. Spectral Analysis: Performs Fast Fourier Transform (FFT) to convert time-domain signals into frequency-domain vibration data.
3. Fault Detection: Monitors a specific "Danger Zone" (2000Hz - 3000Hz). If a spike exceeds the threshold, the system triggers a visual alarm.
4. Pre-Trigger Logging: Utilizes a circular buffer to save the *last 5 seconds* of data leading up to the crash (Event-Triggered Logging).
5. Forensics Mode: Includes a Replay Tool to load crash logs (`.wav`) and analyze the failure frame-by-frame.

## 💻 How to Run
1.  Clone the repository:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/Industrial-Acoustic-Twin.git](https://github.com/YOUR_USERNAME/Industrial-Acoustic-Twin.git)
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the Main Controller:
    ```bash
    python main.py
    ```

## 📂 Project Structure
* `main.py` - Central launcher application.
* `live_monitor.py` - The Sensor/DAQ logic.
* `replay_tool.py` - The Post-Mortem analysis tool.
