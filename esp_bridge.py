"""
esp_bridge.py
TCP <--> ESP32 bridge that also (optionally) serves WebSocket clients *and*
publishes every parsed JSON packet into `gui_queue` so a PyQt GUI can read it.
"""

import queue
import random
import socket
import json
import threading
from pynput import keyboard
import time
import asyncio

###################################
# Constants / Globals
###################################
HOST, PORT     = "0.0.0.0", 12346          # raw TCP from ESP
WS_HOST, WS_PORT = "0.0.0.0", 8765         # optional WebSocket
START_ID, STOP_ID = 0x32, 0x33

KEY_SIGNAL = False
CHAR       = None
esp_sending_json = False
send_start_flag = send_stop_flag = estop_flag = False
last_json_time  = 0

commands_from_gui = queue.Queue()  # GUI → start/stop
gui_queue         = queue.Queue()  # bridge → GUI  🔹

client_socket = None               # ESP TCP socket

###################################
# Keyboard listener (optional debug)
###################################
def on_press(key):
    global KEY_SIGNAL, CHAR
    try:
        if key.char:
            CHAR, KEY_SIGNAL = key.char.lower(), True
    except AttributeError:
        pass

def listen_for_keys():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

###################################
# TCP server ←→ ESP32
###################################
def start_server():
    global client_socket, send_start_flag, send_stop_flag, estop_flag
    global esp_sending_json, last_json_time, KEY_SIGNAL, CHAR

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind((HOST, PORT))
    srv.listen(1)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print(f"[SERVER] listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = srv.accept()
        print("[SERVER] connected from", addr)
        client_socket.settimeout(0.5)
        break

    while True:
        # ------------------------------------------------------------------
        # consume GUI->bridge commands
        try:
            while True:
                cmd = commands_from_gui.get_nowait()
                if cmd == "start":
                    print("[BRIDGE] Received start command from GUI")
                    send_start_flag, send_stop_flag = True, False
                elif cmd == "stop":
                    print("[BRIDGE] Received stop command from GUI")
                    send_stop_flag, send_start_flag = True, False
        except queue.Empty:
            pass
        # keyboard shortcuts (optional)
        if KEY_SIGNAL and not estop_flag:
            if CHAR == "s":
                print("[BRIDGE] Start key pressed")
                send_start_flag, send_stop_flag = True, False
            elif CHAR == "t":
                print("[BRIDGE] Stop key pressed")
                send_stop_flag, send_start_flag = True, False
            KEY_SIGNAL = False
        # ------------------------------------------------------------------
        # transmit START/STOP frames when appropriate
        if send_start_flag and not esp_sending_json:
            print("[BRIDGE] Sending START frame to ESP")
            client_socket.sendall(bytes([0x02, START_ID, 0x03]))
            time.sleep(0.1)
        if send_stop_flag and esp_sending_json:
            print("[BRIDGE] Sending STOP frame to ESP")
            client_socket.sendall(bytes([0x02, STOP_ID, 0x03]))
            time.sleep(0.1)
        # ------------------------------------------------------------------
        # receive from ESP
        try:
            buf = client_socket.recv(1024)
        except socket.timeout:
            buf = b""
        if not buf:
            time.sleep(0.05)
            continue

        if buf.startswith(b"\x02") and buf.endswith(b"\x03"):
            payload = buf[1:-1]
            if not payload:
                continue
            msg_id, json_raw = payload[0], payload[1:].decode(errors="ignore")
            json_start, json_end = json_raw.find("{"), json_raw.rfind("}")
            if json_start != -1 and json_end != -1:
                try:
                    parsed = json.loads(json_raw[json_start:json_end+1])
                    esp_sending_json, last_json_time = True, time.time()
                    if send_start_flag:
                        send_start_flag = False
                    # 🔹 push to GUI
                    gui_queue.put(parsed)

                except json.JSONDecodeError:
                    print("[SERVER] bad JSON")
        time.sleep(0.05)

###################################
# bootstrap if run standalone
###################################
if __name__ == "__main__":
    threading.Thread(target=listen_for_keys, daemon=True).start()
    start_server()
