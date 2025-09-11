"""
Main Tab
High-level overview tab with key system gauges.
"""

from PyQt5.QtWidgets import QWidget, QGridLayout
from widgets.linear_gauge import LinearGauge

class MainTab(QWidget):
    """Main tab with high-level information"""
    
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
        self.pump_temp = LinearGauge("Pump Temperature", 0, 100, 15, 75, 0, 85, "°C")
        self.gas_level = LinearGauge("Explosive Gas", 0, 100, 0, 20, 0, 50, "%")
        
        # Set minimum sizes for gauges
        for gauge in [self.motor_temp, self.cutter_rpm, self.pump_temp, self.gas_level]:
            gauge.setMinimumWidth(450)
            gauge.setMinimumHeight(180)  # Updated to match new height
        
        # Add gauges to layout
        layout.addWidget(self.motor_temp, 0, 0)
        layout.addWidget(self.cutter_rpm, 0, 1)
        layout.addWidget(self.pump_temp, 1, 0)
        layout.addWidget(self.gas_level, 1, 1)
        
        # Set initial values
        self.motor_temp.set_value(25)  # Updated to match 0-50 range
        self.cutter_rpm.set_value(3200)
        self.pump_temp.set_value(45)
        self.gas_level.set_value(15)
        
    def set_machine_state(self, state):
        """Update machine state for all gauges"""
        self.motor_temp.set_machine_state(state)
        self.cutter_rpm.set_machine_state(state)
        self.pump_temp.set_machine_state(state)
        self.gas_level.set_machine_state(state) 