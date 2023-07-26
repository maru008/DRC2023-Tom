import socket
import json
import time
import traceback
from threading import Thread

class VoiceRecognition:
    def __init__(self, DIALOG_MODE, ip, port):
        self.DIALOG_MODE = DIALOG_MODE
        self.ip = ip
        self.port = int(port)

    def recognize(self):
        if self.DIALOG_MODE == "robot_dialog":
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.ip, self.port))
            while True:  # Keep looping until a non-empty result is obtained
                self.listen_once()
                while True:
                    if not self.received_stack:
                        time.sleep(0.1)
                        continue
                    result = self.received_stack.pop(0)
                    if result["type"] in ["final", "failed"] and result["user_utterance"].strip() != "":
                        break
                    elif result["type"] == "silent":
                        self.received_stack.clear()  # Clear the received_stack
                        break  # Break the inner loop to restart listen_once
                if result["type"] in ["final", "failed"] and result["user_utterance"].strip() != "":
                    break
            print(result)
            self.sock.close()
            return result["user_utterance"]
        elif self.DIALOG_MODE == "console_dialog":
            usr_input_text = str(input("user:"))
            return usr_input_text
    
    def _send_command(self, command):
        command_ln = command + "\n"
        self.sock.send(command_ln.encode('utf-8'))

    def _parse_data(self, received_data):
        try:
            received_str = received_data.decode("utf-8")
        except UnicodeDecodeError:
            received_str = "failed:\n"
        if received_str.startswith("startrecog:"):
            return {"type": "start", "user_utterance": "", "confidence": -1}
        elif received_str.startswith("interimresult:"):
            result_str, _ = received_str.split("\n")
            return {"type": "interim", "user_utterance": result_str, "confidence": -1}
        elif received_str.startswith("result:"):
            result_str, confidence_str, _ = received_str.split("\n")
            return {"type": "final", "user_utterance": result_str.lstrip("result:"), "confidence": float(confidence_str.lstrip("confidence:"))}
        elif received_str.startswith("failed:"):
            return {"type": "failed", "user_utterance": "", "confidence": -1}

    def listener(self):
        self.received_stack = []
        self.start_listen()
        try:
            while True:
                received_data = self.sock.recv(1024)
                received = self._parse_data(received_data)
                self.received_stack.append(received)
                if received["type"] in ["failed", "final"]:
                    break
        except socket.timeout:
            self.received_stack.append( {"type": "silent", "user_utterance": "", "confidence": -1} )
        self.stop_listen()

    def start_listen(self):
        command = "start"
        self._send_command(command)
        print("VoiceRecognition: start listening")

    def stop_listen(self):
        command = "stop"
        self._send_command(command)
        print("VoiceRecognition: stop listening")

    def listen_once(self, silent_interval=3):
        self.sock.settimeout(silent_interval)
        self.listener()  # Call the listener method directly
