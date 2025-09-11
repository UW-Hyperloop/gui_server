"""
Engine Tab
Detailed engine and cutterhead monitoring tab.
"""

from PyQt5.QtWidgets import QWidget, QGridLayout
from widgets.linear_gauge import LinearGauge

class EngineTab(QWidget):
    """Engine/Cutterhead tab with detailed motor information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # Increased margins
        layout.setSpacing(30)  # Increased spacing between gauges
        
        # Create gauges with proper sizing
        self.motor_temp = LinearGauge("Motor Temperature", 0, 50, 0, 40, 0, 45, "°C")
        self.cutter_rpm = LinearGauge("Cutter Head RPM", 0, 5000, 1000, 4000, 0, 4500, "RPM")
        self.cutter_voltage = LinearGauge("Cutter Head Voltage", 0, 600, 400, 550, 0, 580, "V")
        
        # Set minimum sizes for gauges
        for gauge in [self.motor_temp, self.cutter_rpm, self.cutter_voltage]:
            gauge.setMinimumWidth(450)
            gauge.setMinimumHeight(180)  # Updated to match new height
        
        # Add gauges to layout
        layout.addWidget(self.motor_temp, 0, 0)
        layout.addWidget(self.cutter_rpm, 0, 1)
        layout.addWidget(self.cutter_voltage, 1, 0, 1, 2)
        
        # Set initial values
        self.motor_temp.set_value(25)  # Updated to match 0-50 range
        self.cutter_rpm.set_value(3200)
        self.cutter_voltage.set_value(480)
        
    def set_machine_state(self, state):
        """Update machine state for all gauges"""
        self.motor_temp.set_machine_state(state)
        self.cutter_rpm.set_machine_state(state)
        self.cutter_voltage.set_machine_state(state) 