"""
Data Simulator
Provides realistic simulation data for the TBM GUI.
"""

import random
import math
from PyQt5.QtCore import QTimer

class DataSimulator:
    """Simulates realistic TBM data"""
    
    def __init__(self, main_tab, engine_tab, pump_tab, navigation_tab, terminal):
        self.main_tab = main_tab
        self.engine_tab = engine_tab
        self.pump_tab = pump_tab
        self.navigation_tab = navigation_tab
        self.terminal = terminal
        
        # Initialize simulation values
        self.motor_temp = 25.0
        self.cutter_rpm = 3200.0
        self.pump_temp = 45.0
        self.explosive_gas = 15.0
        self.cutter_voltage = 480.0
        self.coolant_flow = 120.0
        self.soil_treatment_flow = 122.0
        
        # 6DOF simulation values
        self.x_position = 0.0
        self.y_position = 0.0
        self.z_position = 0.0
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        
        # Simulation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # Update every second
        
        # Log initial message
        self.terminal.log_message("System initialized", "INFO")
        
    def update_data(self):
        """Update all simulation data"""
        # Update main tab data
        self.update_main_tab()
        
        # Update engine tab data
        self.update_engine_tab()
        
        # Update pump tab data
        self.update_pump_tab()
        
        # Update navigation tab data
        self.update_navigation_tab()
        
    def update_main_tab(self):
        """Update main tab gauges"""
        # Motor temperature (0-50°C, safe: 0-40°C)
        self.motor_temp += random.uniform(-2, 2)
        self.motor_temp = max(20, min(50, self.motor_temp))
        self.main_tab.motor_temp.set_value(self.motor_temp)
        
        # Cutter head RPM (0-5000, safe: 0-4000)
        self.cutter_rpm += random.uniform(-100, 100)
        self.cutter_rpm = max(3000, min(5000, self.cutter_rpm))
        self.main_tab.cutter_rpm.set_value(self.cutter_rpm)
        
        # Pump temperature (0-100°C, safe: 0-75°C)
        self.pump_temp += random.uniform(-3, 3)
        self.pump_temp = max(40, min(100, self.pump_temp))
        self.main_tab.pump_temp.set_value(self.pump_temp)
        
        # Explosive gas (0-100%, safe: 0-20%)
        self.explosive_gas += random.uniform(-1, 1)
        self.explosive_gas = max(10, min(30, self.explosive_gas))
        self.main_tab.gas_level.set_value(self.explosive_gas)
        
        # Log warnings
        if self.motor_temp > 40:
            self.terminal.log_message("Motor temperature is high!", "WARNING")
        if self.pump_temp > 75:
            self.terminal.log_message("Pump temperature is high!", "WARNING")
        if self.explosive_gas > 20:
            self.terminal.log_message("Explosive gas levels are high!", "WARNING")
            
    def update_engine_tab(self):
        """Update engine tab gauges"""
        # Motor temperature (same as main tab)
        self.engine_tab.motor_temp.set_value(self.motor_temp)
        
        # Cutter head RPM (same as main tab)
        self.engine_tab.cutter_rpm.set_value(self.cutter_rpm)
        
        # Cutter head voltage (400-600V, safe: 450-550V)
        self.cutter_voltage += random.uniform(-10, 10)
        self.cutter_voltage = max(400, min(600, self.cutter_voltage))
        self.engine_tab.cutter_voltage.set_value(self.cutter_voltage)
        
    def update_pump_tab(self):
        """Update pump tab gauges"""
        # Pump temperature (same as main tab)
        self.pump_tab.pump_temp.set_value(self.pump_temp)
        
        # Coolant flow (50-200 L/min, safe: 80-150 L/min)
        self.coolant_flow += random.uniform(-5, 5)
        self.coolant_flow = max(50, min(200, self.coolant_flow))
        self.pump_tab.coolant_flow.set_value(self.coolant_flow)
        
        # Soil treatment flow (0-150 L/min, safe: 0-115 L/min)
        self.soil_treatment_flow += random.uniform(-2, 2)
        self.soil_treatment_flow = max(100, min(150, self.soil_treatment_flow))
        self.pump_tab.soil_flow.set_value(self.soil_treatment_flow)
        
        # Log warnings
        if self.coolant_flow < 80 or self.coolant_flow > 150:
            self.terminal.log_message("Water flow rate IN is too high!", "WARNING")
        if self.soil_treatment_flow > 115:
            self.terminal.log_message("Water flow rate OUT Soil Treatment Pump is too high!", "WARNING")
            
    def update_navigation_tab(self):
        """Update navigation tab 6DOF data"""
        # Position simulation (gradual movement)
        self.x_position += random.uniform(-0.5, 0.5)  # Forward/backward movement
        self.y_position = 0.0  # Fixed at 0
        self.z_position = 0.0  # Fixed at 0
        
        # Keep position within reasonable bounds
        self.x_position = max(0, min(30, self.x_position))
        self.y_position = max(-5, min(5, self.y_position))
        self.z_position = max(-5, min(5, self.z_position))
        
        # Orientation simulation (fixed values)
        self.roll = 0.0  # Fixed at 0
        self.pitch = 0.0  # Fixed at 0
        self.yaw = 0.0  # Fixed at 0
        
        # Update navigation tab
        self.navigation_tab.update_6dof_state(
            self.x_position, self.y_position, self.z_position,
            self.roll, self.pitch, self.yaw
        ) 