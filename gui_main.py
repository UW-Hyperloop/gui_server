"""
motor_gui_main.py
Starts the ESP bridge (esp_bridge.py) in a background thread and
opens a PyQt window with the live MotorTempGauge.
"""

import sys, threading, queue
from PyQt5.QtCore    import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider

from esp_bridge import start_server, gui_queue      # ← same object
from motor_temp_gauge import MotorTempGauge

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
        self.setWindowTitle("Motor Temperature – Live")

        self.gauge  = MotorTempGauge(self)
        self.status = QLabel("Status: Running", alignment=Qt.AlignCenter)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 500)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(
            lambda v: self.gauge.set_value(v / 10)
        )

        lay = QVBoxLayout(self)
        lay.addWidget(self.gauge)
        lay.addWidget(self.status)
        lay.addWidget(self.slider)

        bridge.new_data.connect(self._update_from_esp)

    # slot
    def _update_from_esp(self, pkt: dict):
        temp  = pkt.get("motor_temperature")
        state = pkt.get("state", "running")

        if temp is not None:
            self.gauge.set_value(temp)
            self.slider.blockSignals(True)
            self.slider.setValue(int(temp * 10))
            self.slider.blockSignals(False)

        self.gauge.set_machine_state(state)
        self.status.setText(f"Status: {state.capitalize()}")

# ---------------- boot ----------------
def main():
    # launch TCP bridge
    threading.Thread(target=start_server, daemon=True).start()

    app     = QApplication(sys.argv)
    bridge  = BridgeToQt(gui_queue)  # same queue from esp_bridge
    window  = MainWindow(bridge)
    window.resize(650, 250)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
