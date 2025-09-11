"""
System Status Widget
Handles system status indicators and power control buttons.
"""

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
from PyQt5.QtGui import QFont

# System states
SYSTEM_STATES = {
    'ESTOP': 'E-Stop',
    'POWER_OFF': 'Power Off', 
    'POWERING_ON': 'Powering On',
    'RUNNING': 'Running',
    'STOPPING': 'Stopping',
    'ERROR': 'Error'
}

class SystemStatusWidget(QWidget):
    """System status indicator with power buttons"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_state = 'POWER_OFF'
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # System Status section
        status_frame = QFrame()
        status_frame.setFrameShape(QFrame.StyledPanel)
        status_layout = QVBoxLayout(status_frame)
        
        # Title
        title = QLabel("System Status")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        status_layout.addWidget(title)
        
        # Single status indicator with container widget
        indicators_container = QWidget()
        indicators_layout = QHBoxLayout(indicators_container)
        indicators_layout.setSpacing(10)  # Small spacing between dot and label
        
        # Single status indicator with dot and label
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Arial", 20))
        self.status_indicator.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Fixed size - only as wide as content
        
        self.status_label = QLabel("Power Off")
        self.status_label.setFont(QFont("Arial", 18, QFont.Bold))  # Bigger and bold font
        self.status_label.setStyleSheet("color: white;")
        
        indicators_layout.addWidget(self.status_indicator)
        indicators_layout.addWidget(self.status_label)
        
        status_layout.addWidget(indicators_container)
        layout.addWidget(status_frame)
        
        # Add spacing between status and power buttons
        layout.addSpacing(20)
        
        # Power buttons
        power_frame = QFrame()
        power_frame.setFrameShape(QFrame.StyledPanel)
        power_layout = QHBoxLayout(power_frame)  # Changed to horizontal layout
        
        self.power_on_btn = QPushButton("POWER ON")
        self.power_off_btn = QPushButton("POWER OFF")
        
        self.power_on_btn.setMinimumHeight(50)
        self.power_off_btn.setMinimumHeight(50)
        
        # Set larger fonts for power buttons
        power_font = QFont("Arial", 14, QFont.Bold)
        self.power_on_btn.setFont(power_font)
        self.power_off_btn.setFont(power_font)
        
        self.power_on_btn.setStyleSheet("""
            QPushButton {
                background-color: #00AA00;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:pressed {
                background-color: #008800;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #808080;
            }
        """)
        
        self.power_off_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF4F4F;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:pressed {
                background-color: #CC3C3C;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #808080;
            }
        """)
        
        power_layout.addWidget(self.power_on_btn)
        power_layout.addWidget(self.power_off_btn)
        
        layout.addWidget(power_frame)
        
        # Connect signals
        self.power_on_btn.clicked.connect(self.power_on)
        self.power_off_btn.clicked.connect(self.power_off)
        
    def set_state(self, state):
        self.current_state = state
        self.update_ui()
        
    def update_ui(self):
        # Update single status indicator based on state
        state_text = SYSTEM_STATES.get(self.current_state, self.current_state)
        self.status_label.setText(state_text)
        
        # Set color based on state
        if self.current_state == 'RUNNING':
            self.status_indicator.setStyleSheet("color: #00FF00;")  # Green
        elif self.current_state == 'POWER_OFF':
            self.status_indicator.setStyleSheet("color: #808080;")  # Grey
        elif self.current_state == 'ERROR':
            self.status_indicator.setStyleSheet("color: #FF4F4F;")  # Red
        elif self.current_state == 'ESTOP':
            self.status_indicator.setStyleSheet("color: #FF4F4F;")  # Red
        elif self.current_state == 'POWERING_ON':
            self.status_indicator.setStyleSheet("color: #FFA500;")  # Orange
        elif self.current_state == 'STOPPING':
            self.status_indicator.setStyleSheet("color: #FFA500;")  # Orange
        else:
            self.status_indicator.setStyleSheet("color: #808080;")  # Grey
        
        # Update button states
        self.power_on_btn.setEnabled(self.current_state == 'POWER_OFF')
        self.power_off_btn.setEnabled(self.current_state in ['RUNNING', 'POWERING_ON'])
        
    def power_on(self):
        self.set_state('POWERING_ON')
        # Simulate power on sequence
        QTimer.singleShot(2000, lambda: self.set_state('RUNNING'))
        
    def power_off(self):
        self.set_state('STOPPING')
        # Simulate power off sequence
        QTimer.singleShot(1000, lambda: self.set_state('POWER_OFF'))
        
    def stop_machine(self):
        self.set_state('ESTOP')
        # Simulate emergency stop
        QTimer.singleShot(500, lambda: self.set_state('ERROR')) 