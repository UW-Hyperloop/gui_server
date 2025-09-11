"""
Navigation Tab
Displays the machine's 6 degrees of freedom (6DOF) state including position and orientation.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QPushButton, QSlider
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class NavigationTab(QWidget):
    """Navigation tab showing 6DOF state"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_segment = 0  # Current wall segment (0-30)
        self.segment_length = 1.0  # Length of each wall segment in meters
        self.push_state = "idle"  # idle, pushing, complete
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Push Control Section
        self.setup_push_controls(layout)
        
        # Add summary section
        self.setup_summary_section(layout)
        
    def setup_push_controls(self, layout):
        """Setup push control panel with buttons and progress slider"""
        push_frame = QFrame()
        push_frame.setFrameShape(QFrame.StyledPanel)
        push_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #404040;
                border-radius: 5px;
                background-color: #2C2C2C;
            }
        """)
        
        push_layout = QVBoxLayout(push_frame)
        push_layout.setSpacing(15)
        
        # Push Control Title
        push_title = QLabel("Wall Lining Propulsion Control")
        push_title.setFont(QFont("Arial", 14, QFont.Bold))
        push_title.setStyleSheet("color: white;")
        push_title.setMaximumHeight(80)
        push_layout.addWidget(push_title)
        
        # Push Buttons
        button_layout = QHBoxLayout()
        
        self.start_push_btn = QPushButton("START Segment Push")
        self.stop_push_btn = QPushButton("STOP Segment Push")
        
        self.start_push_btn.setMinimumHeight(40)
        self.start_push_btn.setMaximumWidth(300)
        self.stop_push_btn.setMinimumHeight(40)
        self.stop_push_btn.setMaximumWidth(300)
        
        self.start_push_btn.setStyleSheet("""
            QPushButton {
                background-color: #00AA00;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:pressed {
                background-color: #008800;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #808080;
            }
        """)
        
        self.stop_push_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF4F4F;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:pressed {
                background-color: #CC3C3C;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #808080;
            }
        """)
        
        button_layout.addWidget(self.start_push_btn)
        button_layout.addWidget(self.stop_push_btn)
        push_layout.addLayout(button_layout)
        
        # Progress Slider Section
        progress_layout = QVBoxLayout()
        
        # Progress Label
        self.progress_label = QLabel("Wall Segment Progress: 0%")
        self.progress_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.progress_label.setStyleSheet("color: white;")
        progress_layout.addWidget(self.progress_label)
        
        # Progress Slider
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(100)
        self.progress_slider.setValue(0)
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #404040;
                height: 20px;
                background: #1C1C1C;
                border-radius: 10px;
            }
            QSlider::handle:horizontal {
                background: #00FF00;
                border: 1px solid #00FF00;
                width: 30px;
                margin: -5px 0;
                border-radius: 15px;
            }
            QSlider::sub-page:horizontal {
                background: #00AA00;
                border-radius: 10px;
            }
        """)
        
        progress_layout.addWidget(self.progress_slider)
        
        # Segment Info
        self.segment_info = QLabel("Segment: 0/30 | Total Progress: 0.0m")
        self.segment_info.setFont(QFont("Arial", 12))
        self.segment_info.setStyleSheet("color: #00FF00;")
        progress_layout.addWidget(self.segment_info)
        
        push_layout.addLayout(progress_layout)
        layout.addWidget(push_frame)
        
        # Connect signals
        self.start_push_btn.clicked.connect(self.start_push)
        self.stop_push_btn.clicked.connect(self.stop_push)
        self.progress_slider.valueChanged.connect(self.on_progress_changed)
        
        # Initial button states
        self.update_button_states()
        
    def setup_summary_section(self, layout):
        """Setup summary section with current 6DOF values"""
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.StyledPanel)
        summary_frame.setMaximumHeight(300)
        summary_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #404040;
                border-radius: 5px;
                background-color: #2C2C2C;
            }
        """)
        
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setSpacing(30)
        
        
        # Position summary
        pos_layout = QVBoxLayout()
        pos_layout.setSpacing(5)  # Reduced spacing between title and value
        pos_title = QLabel("Current Position")
        pos_title.setFont(QFont("Arial", 18, QFont.Bold))
        pos_title.setStyleSheet("color: white;")
        pos_title.setMaximumHeight(80)
        pos_layout.addWidget(pos_title)
        
        self.pos_summary = QLabel("X: 0.0m | Y: 0.0m | Z: 0.0m")
        self.pos_summary.setFont(QFont("Arial", 16, QFont.Bold))  # Bigger values
        self.pos_summary.setStyleSheet("color: #00FF00;")
        pos_layout.addWidget(self.pos_summary)
        
        summary_layout.addLayout(pos_layout)
        
        # Orientation summary
        orient_layout = QVBoxLayout()
        orient_layout.setSpacing(5)  # Reduced spacing between title and value
        orient_title = QLabel("Current Orientation")
        orient_title.setFont(QFont("Arial", 18, QFont.Bold))
        orient_title.setStyleSheet("color: white;")
        orient_title.setMaximumHeight(80)
        orient_layout.addWidget(orient_title)
        
        self.orient_summary = QLabel("Roll: 0.0° | Pitch: 0.0° | Yaw: 0.0°")
        self.orient_summary.setFont(QFont("Arial", 16, QFont.Bold))  # Bigger values
        self.orient_summary.setStyleSheet("color: #00FF00;")
        orient_layout.addWidget(self.orient_summary)
        
        summary_layout.addLayout(orient_layout)
        
        layout.addWidget(summary_frame)
        
    def start_push(self):
        """Start push operation"""
        self.push_state = "pushing"
        self.update_button_states()
        self.update_segment_info()
        
    def stop_push(self):
        """Stop push operation"""
        self.push_state = "idle"
        
        # Increment segment and reset progress
        if self.progress_slider.value() >= 100:  # Only increment if segment is complete
            self.current_segment += 1
            self.current_segment = min(self.current_segment, 30)  # Cap at 30 segments
        
        # Reset progress slider
        self.progress_slider.setValue(0)
        
        self.update_button_states()
        self.update_segment_info()
        
    def on_progress_changed(self, value):
        """Handle progress slider changes"""
        self.update_segment_info()
        
    def update_button_states(self):
        """Update button enabled/disabled states"""
        if self.push_state == "idle":
            self.start_push_btn.setEnabled(True)
            self.stop_push_btn.setEnabled(False)
        elif self.push_state == "pushing":
            self.start_push_btn.setEnabled(False)
            self.stop_push_btn.setEnabled(True)
            
    def update_segment_info(self):
        """Update segment progress information"""
        progress_percent = self.progress_slider.value()
        self.progress_label.setText(f"Segment Progress: {progress_percent}%")
        
        # Calculate current X position
        current_x = self.current_segment + (progress_percent / 100.0 * self.segment_length)
        
        # Update segment info
        self.segment_info.setText(f"Segment: {self.current_segment}/30 | Total Progress: {current_x:.1f}m")
        
        # Update position summary
        if hasattr(self, 'pos_summary'):
            current_y = getattr(self, '_current_y', 0.0)
            current_z = getattr(self, '_current_z', 0.0)
            self.pos_summary.setText(f"X: {current_x:.1f}m | Y: {current_y:.1f}m | Z: {current_z:.1f}m")
        
    def set_machine_state(self, state):
        """Set machine state for stale data indication"""
        # No gauges to update, but keeping the method for consistency
        pass
        
    def update_6dof_state(self, x, y, z, roll, pitch, yaw):
        """Update all 6DOF values"""
        # Store current values
        self._current_y = y
        self._current_z = z
        
        # Update position summary (X is controlled by progress slider)
        current_x = self.current_segment + (self.progress_slider.value() / 100.0 * self.segment_length)
        self.pos_summary.setText(f"X: {current_x:.1f}m | Y: {y:.1f}m | Z: {z:.1f}m")
        self.orient_summary.setText(f"Roll: {roll:.1f}° | Pitch: {pitch:.1f}° | Yaw: {yaw:.1f}°") 