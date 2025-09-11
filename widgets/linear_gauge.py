"""
Linear Gauge Widget
A customizable linear gauge with safe zones and danger markers.
"""

from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush, QPolygonF

class LinearGauge(QWidget):
    """Linear gauge widget with green safe zone and red danger markers"""
    
    def __init__(self, title, min_val, max_val, safe_min, safe_max, danger_min=None, danger_max=None, unit="", parent=None):
        super().__init__(parent)
        self.title = title
        self.min_val = min_val
        self.max_val = max_val
        self.safe_min = safe_min
        self.safe_max = safe_max
        self.danger_min = danger_min
        self.danger_max = danger_max
        self.unit = unit
        self.value = 0
        self.warning = False
        self.critical = False
        self.machine_state = "running"  # For stale data indication
        
        # Adjusted minimum sizes for better spacing
        self.setMinimumHeight(160)
        self.setMinimumWidth(400)
        
    def set_value(self, value):
        self.value = value
        # Determine warning/critical status
        if value < self.safe_min or value > self.safe_max:
            if (self.danger_min and value <= self.danger_min) or (self.danger_max and value >= self.danger_max):
                self.critical = True
                self.warning = False
            else:
                self.warning = True
                self.critical = False
        else:
            self.warning = False
            self.critical = False
        self.update()
        
    def set_machine_state(self, state):
        self.machine_state = state
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Colors
        bg = QColor("#1C1C1C")
        text_color = QColor("#FFFFFF")
        green = QColor("#00FF00")
        yellow = QColor("#FFA500")
        red = QColor("#FF4F4F")
        grey = QColor("#9F9F9F")
        
        # Layout with better spacing - increased space between title and meter
        width = self.width()
        height = self.height()
        margin = 30
        gauge_height = 30
        title_height = 35
        value_height = 45  # Increased space for value above triangle
        scale_height = 20
        status_height = 20
        
        # Calculate positions to prevent overflow - more space between title and meter
        gauge_y = title_height + value_height + 25  # Increased from 15 to 25
        scale_y = gauge_y + gauge_height + 5
        status_y = scale_y + scale_height + 20  # Increased from 10 to 20 to move status lower
        
        # Background
        painter.fillRect(self.rect(), bg)
        
        # Title - positioned to avoid overlap with value
        painter.setPen(text_color)
        painter.setFont(QFont("Arial", 16))
        # Position title on the left side, leaving space for value on the right
        title_rect = QRectF(margin, 10, width // 2 - margin, title_height)
        painter.drawText(title_rect, Qt.AlignLeft, self.title)
        
        # Gauge background (the meter)
        gauge_rect = QRectF(margin, gauge_y, width - 2*margin, gauge_height)
        painter.setPen(QPen(text_color, 1))
        painter.drawRect(gauge_rect)
        
        # Calculate positions
        gauge_width = width - 2*margin
        safe_min_pos = margin + (self.safe_min - self.min_val) / (self.max_val - self.min_val) * gauge_width
        safe_max_pos = margin + (self.safe_max - self.min_val) / (self.max_val - self.min_val) * gauge_width
        current_pos = margin + (self.value - self.min_val) / (self.max_val - self.min_val) * gauge_width
        
        # Ensure positions are within bounds
        safe_min_pos = max(margin, min(width - margin, safe_min_pos))
        safe_max_pos = max(margin, min(width - margin, safe_max_pos))
        current_pos = max(margin, min(width - margin, current_pos))
        
        # Draw grid lines (dashed lines every 5% of range, solid every 25%)
        grid_divisions = 50  # Total grid divisions
        for i in range(grid_divisions + 1):
            pos = margin + (i / grid_divisions) * gauge_width
            
            # Solid lines every 5th division (every 25% of range)
            if i % 5 == 0:
                painter.setPen(QPen(text_color, 1, Qt.SolidLine))
            else:
                painter.setPen(QPen(QColor(255, 255, 255, 25), 1, Qt.DashLine))
            
            painter.drawLine(int(pos), gauge_y, int(pos), gauge_y + gauge_height)
        
        # Draw red background overlay when value exceeds safe range
        if self.value > self.safe_max:
            red_start = safe_max_pos
            red_end = current_pos
            red_rect = QRectF(red_start, gauge_y, red_end - red_start, gauge_height)
            painter.fillRect(red_rect, QColor(red.red(), red.green(), red.blue(), 76))  # 30% opacity
        
        # Draw safe zone markers (green vertical lines)
        painter.setPen(QPen(green, 2))
        painter.drawLine(int(safe_min_pos), gauge_y - 15, int(safe_min_pos), gauge_y + gauge_height)
        painter.drawLine(int(safe_max_pos), gauge_y - 15, int(safe_max_pos), gauge_y + gauge_height)
        
        # Draw current value marker
        is_stale = self.machine_state != "running"
        if is_stale:
            marker_color = grey
        elif self.critical:
            marker_color = red
        elif self.warning:
            marker_color = yellow
        else:
            marker_color = green
            
        # Draw triangle marker above the gauge
        pts = [QPointF(current_pos, gauge_y + 10),
               QPointF(current_pos - 8, gauge_y - 20),
               QPointF(current_pos + 8, gauge_y - 20)]
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(marker_color))
        painter.drawPolygon(QPolygonF(pts))
        
        # Draw current value above the triangle - positioned to show where it is on the gauge
        painter.setPen(marker_color)
        painter.setFont(QFont("Arial", 20, QFont.Bold))
        value_text = f"{self.value:.0f}"
        # Position value above the triangle to show its position on the gauge
        value_rect = QRectF(current_pos - 40, gauge_y - 55, 80, 25)
        painter.drawText(value_rect, Qt.AlignCenter, value_text)
        
        # Draw scale numbers below the gauge with improved positioning
        painter.setPen(grey)
        painter.setFont(QFont("Arial", 12))  # Slightly smaller font
        
        # Calculate scale divisions based on range
        range_size = self.max_val - self.min_val
        
        # For large ranges (like RPM), use fewer divisions
        if range_size > 1000:
            # For RPM (0-5000), show: 0, 1000, 2000, 3000, 4000, 5000
            scale_values = [0, 1000, 2000, 3000, 4000, 5000] if self.max_val == 5000 else [0, 1000, 2000, 3000, 4000, 5000]
        elif range_size > 100:
            # For medium ranges, show every 25% of range
            scale_values = [self.min_val + i * range_size / 4 for i in range(5)]
        else:
            # For small ranges, show every 20% of range
            scale_values = [self.min_val + i * range_size / 5 for i in range(6)]
        
        # Create set of boundary values to avoid double labels
        boundary_values = {self.safe_min, self.safe_max}
        
        for i, val in enumerate(scale_values):
            # Calculate position
            pos = margin + (val - self.min_val) / (self.max_val - self.min_val) * gauge_width
            
            # Ensure position is within bounds
            pos = max(margin, min(width - margin, pos))
            
            # Format text
            if val >= 1000:
                text = f"{val:.0f}"
            else:
                text = f"{val:.0f}"
            
            # Calculate text width for proper centering
            text_rect = painter.fontMetrics().boundingRect(text)
            text_width = text_rect.width()
            
            # Position text with proper centering and bounds checking
            text_x = pos - text_width // 2
            text_x = max(margin, min(width - margin - text_width, text_x))
            
            # Only draw scale numbers that are NOT boundary values (to avoid double labels)
            if val not in boundary_values:
                painter.drawText(int(text_x), scale_y + 15, text)
        
        # Draw safe zone labels BELOW the meter (not above)
        painter.setPen(green)
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        
        # Safe min label below the meter
        safe_min_text = f"{self.safe_min:.0f}"
        safe_min_rect = QRectF(safe_min_pos - 30, scale_y + 15, 60, 20)
        painter.drawText(safe_min_rect, Qt.AlignCenter, safe_min_text)
        
        # Safe max label below the meter
        safe_max_text = f"{self.safe_max:.0f}"
        safe_max_rect = QRectF(safe_max_pos - 30, scale_y + 15, 60, 20)
        painter.drawText(safe_max_rect, Qt.AlignCenter, safe_max_text)
        
        # Draw status message closer to the meter
        status_text = "Stale" if is_stale else "Active"
        painter.setPen(text_color)
        painter.setFont(QFont("Arial", 14))
        status_rect = QRectF(margin, status_y, width - 2*margin, status_height)
        painter.drawText(status_rect, Qt.AlignCenter, f"Status: {status_text}") 