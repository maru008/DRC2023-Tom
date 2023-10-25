import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
dialog_modules_dir = os.path.join(current_dir, '..', 'DialogModules')
sys.path.append(dialog_modules_dir)

import socket
import json
import traceback
from DialogModules.Add_Hesitation import add_hesitation

class SpeechGeneration:
    def __init__(self, DIALOG_MODE,ADD_HESITATION, ip, port):
        self.DIALOG_MODE = DIALOG_MODE
        self.ADD_HESITATION = ADD_HESITATION
        self.ip = ip
        self.port = int(port)

    def _send_command(self, command):
        command_ln = command + "\n"
        self.sock.send(command_ln.encode('utf-8'))

    def speech_generate(self, text):
        print("System> ",text)
        if self.DIALOG_MODE == "robot_dialog":
            if self.ADD_HESITATION:
                #いい淀み付与コードの実行
                text = add_hesitation(text)
                
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.sock.connect((self.ip, self.port))
                
                command_dict = {
                    "engine": "POLLY-SSML",
                    "speaker": "Mizuki",
                    "duration-information": False,
                    "speechmark": False,
                    "text": "<speak>" + text.replace("$", "<break time=\"0.2s\"/>") + "</speak>"
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
            pass
