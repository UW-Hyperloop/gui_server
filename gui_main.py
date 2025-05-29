"""
motor_gui_main.py
Starts the ESP bridge (esp_bridge.py) in a background thread and
opens a PyQt window with multiple gauges for different sensors.
"""

import sys, threading, queue
from PyQt5.QtCore    import Qt, QTimer, pyqtSignal, QObject, QRectF, QPointF
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QSlider, QPushButton, QGridLayout, QFrame)
from PyQt5.QtGui     import QIcon, QFont, QPainter, QColor, QPen, QBrush, QPolygonF

from esp_bridge import start_server, gui_queue, commands_from_gui      # ← same object
from motor_temp_gauge import MotorTempGauge

# Create copies of the gauge for different sensor types
class PumpTempGauge(MotorTempGauge):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pump Temperature")

class CutterRPMGauge(MotorTempGauge):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cutter RPM")
        self.min_value, self.max_value = 0.0, 5000.0  # Different scale for RPM
        
    def paintEvent(self, event):
        # Override to adjust the scale for RPM (0-5000)
        W = self.width()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # colours
        bg   = QColor("#1C1C1C")
        line = QColor("#ffffff")
        green, red, grey = QColor("#00ff00"), QColor("#FF4F4F"), QColor("#9F9F9F")

        # layout metrics
        g_h, top = 30, 60
        left, right = 10, 10
        g_w = W - left - right
        gauge_rect = QRectF(left, top, g_w, g_h)

        # background & frame
        painter.fillRect(self.rect(), bg)
        painter.setPen(QPen(line, 1))
        painter.drawRect(gauge_rect)

        # grid - adjusted for 0-5000 scale with 500 unit steps
        for i in range(11):  # 0, 500, 1000, ..., 5000
            x = left + i / 10 * g_w
            painter.setPen(QPen(line if i % 2 == 0 else QColor(255, 255, 255, 40),
                                1, Qt.SolidLine if i % 2 == 0 else Qt.DashLine))
            painter.drawLine(int(x), top, int(x), top + g_h)
            
            # Add labels below each marker, but skip thresholds
            if i % 2 == 0 and i not in (0, 8):  # 0 and 4000 are thresholds
                painter.setPen(line)
                painter.setFont(QFont("Arial", 8))
                painter.drawText(int(x) - 20, top + g_h + 5, 40, 15, Qt.AlignCenter, str(i*500))

        # scale markers 0 and 4000 - inside the meter with labels below
        for pos, pos_val in [(0, 0), (8, 4000)]:  # Index 8 is 4000 RPM (threshold)
            x = left + pos / 10 * g_w
            # Draw vertical line inside the meter with threshold color
            painter.setPen(QPen(green if pos == 0 else red, 2))
            painter.drawLine(int(x), top, int(x), top + g_h)
            
            # Draw label directly below the meter
            painter.setPen(green if pos == 0 else red)
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            painter.drawText(int(x) - 20, top + g_h + 5, 40, 15, Qt.AlignCenter, str(pos_val))

        # red overlay
        if self.value > 4000:
            x0 = left + 8 / 10 * g_w  # 4000 RPM position
            x1 = left + min(self.value / 5000, 1.0) * g_w
            painter.fillRect(QRectF(x0, top, x1 - x0, g_h),
                             QColor(red.red(), red.green(), red.blue(), 76))

        # pointer
        pos_x = left + (self.value / 5000) * g_w
        stale = self.machine_state != "running"
        color = grey if stale else (red if self.value > 4000 else green)
        
        # Draw value above the triangle
        painter.setPen(color)
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.drawText(int(pos_x) - 30, top - 45, 60, 20,
                         Qt.AlignCenter, f"{self.value:.0f}")
        
        # Draw triangle above the meter pointing down
        pts = [QPointF(pos_x, top + 10),
               QPointF(pos_x - 8, top - 20),
               QPointF(pos_x + 8, top - 20)]
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawPolygon(QPolygonF(pts))

        painter.end()

class GasSensorGauge(MotorTempGauge):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gas Sensor")
        self.min_value, self.max_value = 0.0, 100.0  # Percentage scale

# ---------------- Qt helper to drain the queue ----------------
class BridgeToQt(QObject):
    new_data = pyqtSignal(dict)

    def __init__(self, q: queue.Queue):
        super().__init__()
        self._q = q
        self._tmr = QTimer(self)
        self._tmr.timeout.connect(self._drain)
        self._tmr.start(50)

    def _drain(self):
        try:
            while True:
                self.new_data.emit(self._q.get_nowait())
        except queue.Empty:
            pass

# ---------------- MainWindow ----------------
class MainWindow(QWidget):
    def __init__(self, bridge: BridgeToQt):
        super().__init__()
        self.setWindowTitle("Machine Monitoring Dashboard")
        self.setFocusPolicy(Qt.StrongFocus)  # Enable keyboard focus
        self.setFocus()  # Set focus to this window
        
        # Create gauges
        self.motor_gauge = MotorTempGauge(self)
        self.motor_gauge.setMinimumWidth(300)
        self.pump_gauge = PumpTempGauge(self)
        self.pump_gauge.setMinimumWidth(300)
        self.rpm_gauge = CutterRPMGauge(self)
        self.rpm_gauge.setMinimumWidth(300)
        self.gas_gauge = GasSensorGauge(self)
        self.gas_gauge.setMinimumWidth(300)
        
        # Labels for each gauge
        self.motor_label = QLabel("Motor Temperature (°C)", alignment=Qt.AlignCenter)
        self.motor_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.pump_label = QLabel("Pump Temperature (°C)", alignment=Qt.AlignCenter)
        self.pump_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.rpm_label = QLabel("Cutter RPM", alignment=Qt.AlignCenter)
        self.rpm_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.gas_label = QLabel("Gas Sensor (%)", alignment=Qt.AlignCenter)
        self.gas_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        # Status indicator
        self.status = QLabel("Status: Running", alignment=Qt.AlignCenter)
        self.status.setFont(QFont("Arial", 14, QFont.Bold))
        
        # Power button
        self.power_button = QPushButton("Power OFF")
        self.power_button.setMinimumHeight(60)
        self.power_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.power_button.setStyleSheet(
            "QPushButton { background-color: #FF4F4F; color: white; border-radius: 10px; }"
            "QPushButton:pressed { background-color: #CC3C3C; }"
        )
        self.power_button.clicked.connect(self.toggle_power)
        self.machine_running = True
        
        # Layout setup - grid layout for 2x2 gauges
        main_layout = QVBoxLayout(self)
        
        # Top section with power button and status
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.power_button)
        top_layout.addWidget(self.status)
        top_layout.setStretch(0, 1)
        top_layout.setStretch(1, 4)
        main_layout.addLayout(top_layout)
        
        # Gauges section
        gauges_layout = QGridLayout()
        
        # Motor temperature gauge in top left
        motor_layout = QVBoxLayout()
        motor_layout.addWidget(self.motor_label)
        motor_layout.addWidget(self.motor_gauge)
        motor_frame = QFrame()
        motor_frame.setFrameShape(QFrame.StyledPanel)
        motor_frame.setLayout(motor_layout)
        gauges_layout.addWidget(motor_frame, 0, 0)
        
        # Pump temperature gauge in top right
        pump_layout = QVBoxLayout()
        pump_layout.addWidget(self.pump_label)
        pump_layout.addWidget(self.pump_gauge)
        pump_frame = QFrame()
        pump_frame.setFrameShape(QFrame.StyledPanel)
        pump_frame.setLayout(pump_layout)
        gauges_layout.addWidget(pump_frame, 0, 1)
        
        # Cutter RPM gauge in bottom left
        rpm_layout = QVBoxLayout()
        rpm_layout.addWidget(self.rpm_label)
        rpm_layout.addWidget(self.rpm_gauge)
        rpm_frame = QFrame()
        rpm_frame.setFrameShape(QFrame.StyledPanel)
        rpm_frame.setLayout(rpm_layout)
        gauges_layout.addWidget(rpm_frame, 1, 0)
        
        # Gas sensor gauge in bottom right
        gas_layout = QVBoxLayout()
        gas_layout.addWidget(self.gas_label)
        gas_layout.addWidget(self.gas_gauge)
        gas_frame = QFrame()
        gas_frame.setFrameShape(QFrame.StyledPanel)
        gas_frame.setLayout(gas_layout)
        gauges_layout.addWidget(gas_frame, 1, 1)
        
        main_layout.addLayout(gauges_layout)
        
        # Set up simulated data for all gauges
        self.motor_gauge.set_value(25.0)
        self.pump_gauge.set_value(22.0)
        self.rpm_gauge.set_value(2500)
        self.gas_gauge.set_value(35.0)
        
        # Connect the bridge signal
        bridge.new_data.connect(self._update_from_esp)

    def keyPressEvent(self, event):
        """Handle keyboard events"""
        print("[GUI] Key pressed:", event.key())  # Debug print
        if event.key() == Qt.Key_S:
            print("[GUI] 'S' key pressed")
            try:
                commands_from_gui.put("start")
                print("[GUI] Start command sent to bridge")
            except Exception as e:
                print("[GUI] Error sending start command:", e)
        elif event.key() == Qt.Key_T:
            print("[GUI] 'T' key pressed")
            try:
                commands_from_gui.put("stop")
                print("[GUI] Stop command sent to bridge")
            except Exception as e:
                print("[GUI] Error sending stop command:", e)
        else:
            super().keyPressEvent(event)

    def focusInEvent(self, event):
        """Called when the window gains focus"""
        print("[GUI] Window gained focus")
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Called when the window loses focus"""
        print("[GUI] Window lost focus")
        super().focusOutEvent(event)

    def toggle_power(self):
        self.machine_running = not self.machine_running
        if self.machine_running:
            self.power_button.setText("Power OFF")
            self.power_button.setStyleSheet(
                "QPushButton { background-color: #FF4F4F; color: white; border-radius: 10px; }"
                "QPushButton:pressed { background-color: #CC3C3C; }"
            )
            self.status.setText("Status: Running")
            self.motor_gauge.set_machine_state("running")
            self.pump_gauge.set_machine_state("running")
            self.rpm_gauge.set_machine_state("running")
            self.gas_gauge.set_machine_state("running")
        else:
            self.power_button.setText("Power ON")
            self.power_button.setStyleSheet(
                "QPushButton { background-color: #00AA00; color: white; border-radius: 10px; }"
                "QPushButton:pressed { background-color: #008800; }"
            )
            self.status.setText("Status: Stopped")
            self.motor_gauge.set_machine_state("stopped")
            self.pump_gauge.set_machine_state("stopped")
            self.rpm_gauge.set_machine_state("stopped")
            self.gas_gauge.set_machine_state("stopped")

    # slot
    def _update_from_esp(self, pkt: dict):
        # Only update if machine is running
        if not self.machine_running:
            return
            
        # Update motor temperature
        motor_temp = pkt.get("motor_temperature")
        if motor_temp is not None:
            self.motor_gauge.set_value(motor_temp)
            
        # Update pump temperature (simulated)
        pump_temp = pkt.get("pump_temperature", motor_temp - 3 if motor_temp else None)
        if pump_temp is not None:
            self.pump_gauge.set_value(pump_temp)
            
        # Update RPM (simulated)
        rpm = pkt.get("cutter_rpm", 2500)
        self.rpm_gauge.set_value(rpm)
        
        # Update gas sensor (simulated)
        gas = pkt.get("gas_level", 35)
        self.gas_gauge.set_value(gas)
        
        # Update machine state
        state = pkt.get("state", "running")
        if state != "running":
            self.toggle_power()  # Turn off if ESP reports machine is stopped

# ---------------- boot ----------------
def main():
    # launch TCP bridge
    threading.Thread(target=start_server, daemon=True).start()

    app = QApplication(sys.argv)
    bridge = BridgeToQt(gui_queue)  # same queue from esp_bridge
    window = MainWindow(bridge)
    window.resize(1200, 800)  # Set a reasonable window size
    window.show()  # Show as normal window instead of fullscreen
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
