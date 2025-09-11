"""
Pump Tab
Pump and flow monitoring tab.
"""

from PyQt5.QtWidgets import QWidget, QGridLayout
from widgets.linear_gauge import LinearGauge

class PumpTab(QWidget):
    """Pump tab with flow monitoring"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # Increased margins
        layout.setSpacing(30)  # Increased spacing between gauges
        
        # Create gauges with proper sizing
        self.pump_temp = LinearGauge("Pump Temperature", 0, 100, 15, 75, 0, 85, "°C")
        self.coolant_flow = LinearGauge("Coolant Flow", 0, 230, 75, 115, 0, 180, "L/min")
        self.soil_flow = LinearGauge("Soil Treatment Flow", 0, 230, 75, 115, 0, 180, "L/min")
        
        # Set minimum sizes for gauges
        for gauge in [self.pump_temp, self.coolant_flow, self.soil_flow]:
            gauge.setMinimumWidth(450)
            gauge.setMinimumHeight(180)  # Updated to match new height
        
        # Add gauges to layout
        layout.addWidget(self.pump_temp, 0, 0)
        layout.addWidget(self.coolant_flow, 0, 1)
        layout.addWidget(self.soil_flow, 1, 0, 1, 2)
        
        # Set initial values
        self.pump_temp.set_value(45)
        self.coolant_flow.set_value(95)
        self.soil_flow.set_value(124)
        
    def set_machine_state(self, state):
        """Update machine state for all gauges"""
        self.pump_temp.set_machine_state(state)
        self.coolant_flow.set_machine_state(state)
        self.soil_flow.set_machine_state(state) 