import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFrame

class Launcher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Industrial Twin Control Panel")
        self.resize(350, 250)
        # Industrial CSS Styling
        self.setStyleSheet("""
            QWidget { background-color: #222; color: #EEE; }
            QPushButton { 
                background-color: #444; 
                border: 2px solid #555; 
                padding: 15px; 
                font-size: 14px; 
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #555; border-color: #777; }
        """)
        
        layout = QVBoxLayout()
        
        # Header
        lbl = QLabel("SYSTEM CONTROLLER")
        lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #00FF00; margin-bottom: 10px; qproperty-alignment: AlignCenter;")
        layout.addWidget(lbl)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #444;")
        layout.addWidget(line)
        
        # Button 1: DAQ
        btn1 = QPushButton("🔴 START LIVE MONITOR (DAQ)")
        btn1.setStyleSheet("border: 2px solid #00FF00; color: #00FF00;")
        btn1.clicked.connect(lambda: self.launch("live_monitor.py"))
        layout.addWidget(btn1)
        
        # Button 2: Forensics
        btn2 = QPushButton("▶ LAUNCH REPLAY TOOL")
        btn2.setStyleSheet("border: 2px solid #FFA500; color: #FFA500;")
        btn2.clicked.connect(lambda: self.launch("replay_tool.py"))
        layout.addWidget(btn2)
        
        self.setLayout(layout)

    def launch(self, script_name):
        # This spawns a new independent process for the tool
        subprocess.Popen([sys.executable, script_name])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Launcher()
    win.show()
    sys.exit(app.exec_())