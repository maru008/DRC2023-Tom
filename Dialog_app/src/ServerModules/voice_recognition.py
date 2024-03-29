import socket
import json
import time
import traceback
from copy import deepcopy
from threading import Thread
from .base import Base

class VoiceRecognition(Base):
    def __init__(self, DIALOG_MODE, ip, port, motion_obj,Dialog_mongodb):
        super().__init__(DIALOG_MODE,ip, int(port))
        self.DIALOG_MODE = DIALOG_MODE
        self.ip = ip
        self.port = int(port)

        self.motion_gen = motion_obj
        self.Dialog_mongodb = Dialog_mongodb
    
    def recognize_speach(self):
        confidence_threshold = 0.5  # Set your desired threshold here
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.DIALOG_MODE == "robot_dialog":
            self.start_listen()
            final_results = []
            
            while True:
                received_data = self.sock.recv(1024)
                if not received_data:
                    continue
                self.motion_gen.play_motion("nod_slight")
                result = self._parse_data(received_data)
                # print(result)
                if result["type"] in ["final", "failed"] and result["user_utterance"] != "" and result["confidence"] >= confidence_threshold:
                    # print("User: ", result["user_utterance"])
                    final_results.append(result["user_utterance"])
                    start_time = time.time()  # 現在の時間を記録
                    while True:
                        if time.time() - start_time > 1:  # n秒以上経過したか確認
                            break  # 2秒以上経っていれば、whileループを抜ける

                        # 新しいデータがあるかどうかを確認する
                        self.sock.setblocking(0)  # ノンブロッキングモードに設定
                        try:
                            new_data = self.sock.recv(1024)  # 新しいデータを受け取る
                            if new_data:
                                new_result = self._parse_data(new_data)  # 新しいデータを解析
                                if new_result["type"] in ["final", "failed"] and new_result["user_utterance"] != "" and new_result["confidence"] >= confidence_threshold:
                                    # print("Additional input received: ", new_result["user_utterance"])
                                    final_results.append(result["user_utterance"])
                                    result = new_result  # 更新された結果を保存
                                    start_time = time.time()  # タイマーをリセット
                        except socket.error:
                            pass
                        time.sleep(0.01)  # 短いスリープでループを遅らせる
                    break

            self.stop_listen()
            User_res_text = ' '.join(final_results)
            print("User> ",User_res_text)
            self.Dialog_mongodb.add_to_dialog_log("user",User_res_text)
            return User_res_text

        elif self.DIALOG_MODE == "console_dialog":
            User_res_text = str(input("User> "))
            self.Dialog_mongodb.add_to_dialog_log("user",User_res_text)
            return User_res_text
    
    def _send_command(self, command):
        command_ln = command + "\n"
        self.sock.send(command_ln.encode('utf-8'))

    def _parse_data(self, received_data):
        try:
            received_str = received_data.decode("utf-8")
        except UnicodeDecodeError:
            received_str = "failed:\n"

        result_str = received_str.split("\n")[0]  # Only get the first line

        if received_str.startswith("startrecog:"):
            return {"type": "start", "user_utterance": "", "confidence": -1}
        elif received_str.startswith("interimresult:"):
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
        self.stop_listen()  # この行をコメントアウトまたは削除

    def start_listen(self):
        if not self.is_socket_connected():
            try:
                self.sock.connect((self.ip, self.port))
            except Exception as e:
                print(f"Error connecting to {self.ip}:{self.port}. Details: {e}")
                return

        command = "start"
        self._send_command(command)
        print("VoiceRecognition: start listening")

    def stop_listen(self):
        command = "stop"
        if not self.is_socket_connected():
            try:
                self.sock.connect((self.ip, self.port))
            except Exception as e:
                print(f"Error connecting to {self.ip}:{self.port}. Details: {e}")
                return
        self._send_command(command)
        print("VoiceRecognition: stop listening")

    def listen_once(self, silent_interval=3):
        self.sock.settimeout(silent_interval)
        self.listener()  # Call the listener method directly
    
    def is_socket_connected(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.getpeername()
            return True
        except socket.error:  # Typically raises a socket.error if not connected
            return False
