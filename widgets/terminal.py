"""
Terminal Widget
Provides a logging terminal for system messages and alerts.
"""

from datetime import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QSizePolicy
from PyQt5.QtGui import QFont

class TerminalWidget(QWidget):
    """Terminal widget for logging messages"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)  # Reduced spacing between title and terminal
        
        # Title container to control spacing
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        # Title
        title = QLabel("Terminal")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: white;")
        title.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Only take needed space
        title_layout.addWidget(title)
        
        layout.addWidget(title_container)
        
        # Terminal text area
        self.terminal = QTextEdit()
        self.terminal.setStyleSheet("""
            QTextEdit {
                background-color: #1C1C1C;
                color: white;
                border: 1px solid #404040;
                border-radius: 5px;
                font-family: 'Courier New';
                font-size: 16px;
            }
        """)
        self.terminal.setFixedHeight(250)  # Increased fixed height for terminal
        layout.addWidget(self.terminal)
        
    def log_message(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "WARNING":
            color = "#FFA500"
            icon = "⚠"
        elif level == "ERROR":
            color = "#FF4F4F"
            icon = "🔥"
        else:
            color = "#00FF00"
            icon = "●"
            
        formatted_message = f'<span style="color: {color};">{icon}</span> [{timestamp}] {message}'
        self.terminal.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.terminal.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum()) 