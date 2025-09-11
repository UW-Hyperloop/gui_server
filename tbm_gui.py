"""
Tunnel Boring Machine Operator GUI - Modular Version
A comprehensive monitoring and control interface for TBM operations.
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QSizePolicy
from PyQt5.QtCore import QTimer

# Import modular components
from widgets import SystemStatusWidget, TerminalWidget
from tabs import MainTab, EngineTab, PumpTab, NavigationTab
from simulation import DataSimulator

class TBMGUI(QWidget):
    """Main TBM GUI window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TBM Operator Interface")
        self.setup_ui()
        self.setup_simulation()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1C1C1C;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 0)  # Reduced top margin to bring status closer to top
        layout.setSpacing(0)
        
        # System status bar
        self.status_widget = SystemStatusWidget()
        self.status_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # Fixed height to shrink status
        layout.addWidget(self.status_widget)
        
        # Add spacing between status and tabs
        layout.addSpacing(20)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)  # Allow tabs to expand
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #1C1C1C;
            }
            QTabBar::tab {
                background-color: #2C2C2C;
                color: white;
                padding: 12px 20px;
                margin-right: 2px;
                font-size: 16px;
                font-weight: bold;
                min-width: 180px;
                min-height: 20px;
            }
            QTabBar::tab:selected {
                background-color: #FF4F4F;
            }
            QTabBar::tab:hover {
                background-color: #404040;
            }
        """)
        
        # Create tabs
        self.main_tab = MainTab()
        self.engine_tab = EngineTab()
        self.pump_tab = PumpTab()
        self.navigation_tab = NavigationTab()
        
        self.tab_widget.addTab(self.main_tab, "Main")
        self.tab_widget.addTab(self.engine_tab, "Engine/Cutterhead")
        self.tab_widget.addTab(self.pump_tab, "Pump")
        self.tab_widget.addTab(self.navigation_tab, "Navigation")
        
        layout.addWidget(self.tab_widget)
        
        # Terminal at bottom
        self.terminal = TerminalWidget()
        self.terminal.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # Fixed height, preferred width
        layout.addWidget(self.terminal)
        
        # Connect tab signals
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Connect system status changes to gauge states
        self.status_widget.power_on_btn.clicked.connect(self.on_system_state_change)
        self.status_widget.power_off_btn.clicked.connect(self.on_system_state_change)
        
    def setup_simulation(self):
        """Setup simulation timer for realistic data updates"""
        self.data_simulator = DataSimulator(
            self.main_tab, 
            self.engine_tab, 
            self.pump_tab, 
            self.navigation_tab,
            self.terminal
        )
        
    def on_system_state_change(self):
        """Handle system state changes and update gauge states"""
        state = self.status_widget.current_state
        machine_state = "running" if state in ["RUNNING", "POWERING_ON"] else "stopped"
        
        # Update all tabs with new machine state
        self.main_tab.set_machine_state(machine_state)
        self.engine_tab.set_machine_state(machine_state)
        self.pump_tab.set_machine_state(machine_state)
        self.navigation_tab.set_machine_state(machine_state)
            
    def on_tab_changed(self, index):
        """Handle tab changes"""
        tab_names = ["Main", "Engine/Cutterhead", "Pump", "Navigation"]
        self.terminal.log_message(f"Switched to {tab_names[index]} tab", "INFO")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = TBMGUI()
    window.resize(1200, 800)  # Set reasonable window size
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 
