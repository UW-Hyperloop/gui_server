"""
motor_temp_gauge.py
Reusable PyQt5 widget that draws a horizontal 0–50 °C bar with
grid lines, red danger overlay (>40 °C) and an arrow pointer.
"""

import random, sys, time
from PyQt5.QtCore    import Qt, QRectF, QPointF
from PyQt5.QtGui     import QPainter, QColor, QPen, QFont, QBrush, QPolygonF
from PyQt5.QtWidgets import QWidget, QSizePolicy

class MotorTempGauge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 25.0
        self.min_value, self.max_value = 0.0, 50.0
        self.machine_state = "running"
        self.setMinimumHeight(130)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    # ---------- public API ----------
    def set_value(self, v: float):
        self.value = max(self.min_value, min(self.max_value, v))
        self.update()

    def set_machine_state(self, st: str):
        self.machine_state = st.lower()
        self.update()

    # ---------- painting -------------
    def paintEvent(self, _event):
        W = self.width()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # colours
        bg   = QColor("#1C1C1C")
        line = QColor("#ffffff")
        green, red, grey = QColor("#00ff00"), QColor("#FF4F4F"), QColor("#9F9F9F")

        # layout metrics
        g_h, top = 30, 60  # Adjusted top position to make room for pointer above
        left, right = 10, 10
        g_w = W - left - right
        gauge_rect = QRectF(left, top, g_w, g_h)

        # background & frame
        painter.fillRect(self.rect(), bg)
        painter.setPen(QPen(line, 1))
        painter.drawRect(gauge_rect)

        # grid
        for i in range(51):
            x = left + i / 50 * g_w
            painter.setPen(QPen(line if i % 5 == 0 and i != 40 else QColor(255, 255, 255, 40),
                                1, Qt.SolidLine if i % 5 == 0 and i != 40 else Qt.DashLine))
            painter.drawLine(int(x), top, int(x), top + g_h)
            
            # Add labels below each 5-unit marker, but skip thresholds (0 and 40)
            if i % 5 == 0 and i not in (0, 40):
                painter.setPen(line)
                painter.setFont(QFont("Arial", 8))
                painter.drawText(int(x) - 10, top + g_h + 5, 20, 15, Qt.AlignCenter, str(i))

        # scale markers 0 and 40 - inside the meter with labels below
        for pos in (0, 40):
            x = left + pos / 50 * g_w
            # Draw vertical line inside the meter with threshold color
            painter.setPen(QPen(green if pos == 0 else red, 2))
            painter.drawLine(int(x), top, int(x), top + g_h)
            
            # Draw label directly below the meter
            painter.setPen(green if pos == 0 else red)
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            painter.drawText(int(x) - 10, top + g_h + 5, 20, 15, Qt.AlignCenter, str(pos))

        # red overlay
        if self.value > 40:
            x0 = left + 40 / 50 * g_w
            x1 = left + self.value / 50 * g_w
            painter.fillRect(QRectF(x0, top, x1 - x0, g_h),
                             QColor(red.red(), red.green(), red.blue(), 76))

        # pointer
        pos_x = left + self.value / 50 * g_w
        stale = self.machine_state != "running"
        color = grey if stale else (red if self.value > 40 else green)
        
        # Draw value above the triangle
        painter.setPen(color)
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.drawText(int(pos_x) - 25, top - 45, 50, 20,
                         Qt.AlignCenter, f"{self.value:.1f}")
        
        # Draw triangle above the meter pointing down
        pts = [QPointF(pos_x, top + 10),
               QPointF(pos_x - 8, top - 20),
               QPointF(pos_x + 8, top - 20)]
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawPolygon(QPolygonF(pts))

        painter.end()
