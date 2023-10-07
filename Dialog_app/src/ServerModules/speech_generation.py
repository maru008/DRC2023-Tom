import socket
import json
import time
import traceback

class SpeechGeneration:
    def __init__(self, DIALOG_MODE, ip, port):
        self.DIALOG_MODE = DIALOG_MODE
        self.ip = ip
        self.port = int(port)

    def _send_command(self, command):
        command_ln = command + "\n"
        self.sock.send(command_ln.encode('utf-8'))

    def speech_generate(self, text):
        if self.DIALOG_MODE == "robot_dialog":
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.sock.connect((self.ip, self.port))
                
                command_dict = {
                    "engine": "POLLY-SSML",
                    "speaker": "Mizuki",
                    "duration-information": False,
                    "speechmark": False,
                    "text": "<speak>" + text + "</speak>"
                }
                command = json.dumps(command_dict)
                self._send_command(command)

                buffer = ""
                while True:
                    received = self.sock.recv(1024)
                    buffer += received.decode("utf-8")
                    while '\n' in buffer:
                        message, buffer = buffer.split('\n', 1)
                        received_data = json.loads(message.strip())
                        if "result" in received_data:
                            if received_data["result"] == "success-end":
                                
                                print("SpeechGeneration: End speaking successfully.")
                                return
                            elif received_data["result"] == "failed":
                                print("SpeechGeneration: Failed speaking.")
                                return
            except Exception as e:
                print(f"SpeechGeneration: An error occurred: {e}")
                traceback.print_exc()
            finally:
                self.sock.close()
        elif self.DIALOG_MODE == "console_dialog":
            print(f"robot: {text}")
