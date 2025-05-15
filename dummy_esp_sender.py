"""
dummy_esp_sender.py
Simulates an ESP32 that streams JSON packets to the TCP bridge so the PyQt GUI
can be tested without real hardware.
"""

import socket, json, random, time, sys

HOST, PORT = "127.0.0.1", 12346   # must match esp_bridge.py

MSG_ID_TBM_DATA = 0x35            # same ID the real board uses

def make_packet(temperature: float, state: str = "running") -> bytes:
    """
    Assemble [0x02, MSG_ID, {...json...}, 0x03]
    """
    payload_dict = {
        "motor_temperature": round(temperature, 1),
        "state": state
    }
    json_bytes = json.dumps(payload_dict).encode()
    return bytes([0x02, MSG_ID_TBM_DATA]) + json_bytes + bytes([0x03])

def main():
    print(f"[DUMMY] connecting to {HOST}:{PORT} …")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("[DUMMY] Bridge not running? Start motor_gui_main.py first.")
        sys.exit(1)

    print("[DUMMY] connected – streaming data every 1 s.  Ctrl-C to stop.")
    temp = 25.0
    try:
        while True:
            # random walk ±0.8 °C, clamp to 10–50
            temp += random.uniform(-0.8, 0.8)
            temp = max(10.0, min(50.0, temp))
            packet = make_packet(temp)
            sock.sendall(packet)
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n[DUMMY] stopped by user.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
