import socket
import json
import time
import traceback
from copy import deepcopy
from threading import Thread
from .base import Base

class VoiceRecognition(Base):
    def __init__(self, DIALOG_MODE, ip, port, motion_obj):
        super().__init__(DIALOG_MODE,ip, int(port))
        self.DIALOG_MODE = DIALOG_MODE
        self.ip = ip
        self.port = int(port)
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock = None
        self.motion_gen = motion_obj
        
    # def start_listen(self):
    #     command = "start"
    #     self._send_command(command)
    #     print("GSRClient:: start GSRServer")

    # def stop_listen(self):
    #     command = "stop"
    #     self._send_command(command)
    #     self.server_is_running = False
    #     print("GSRClient::stop GSRServer")

    # def _parse_data(self, received_data):
    #     try:
    #         received_str = received_data.decode("utf-8")
    #     except UnicodeDecodeError:
    #         received_str = "failed:\n"
    #     # print("GSRClient:: Received: {}".format(received_str))
    #     if received_str.startswith("startrecog:"):
    #         return {"type": "start", "user_utterance": "", "confidence": -1}
    #     elif received_str.startswith("interimresult:"):
    #         result_str, _ = received_str.split("\n")
    #         return {"type": "interim", "user_utterance": result_str, "confidence": -1}
    #     elif received_str.startswith("result:"):
    #         # resultを受け取る
    #         result_str, confidence_str, _ = received_str.split("\n")
    #         return {"type": "final", "user_utterance": result_str.lstrip("result:"), "confidence": float(confidence_str.lstrip("confidence:"))}
    #     elif received_str.startswith("failed:"):
    #         return {"type": "failed", "user_utterance": "", "confidence": -1}

    # def listener(self):
    #     self.received_stack = []
    #     received_count = 0

    #     # 1. サーバー起動
    #     self.start_listen()
        
    #     try:
    #         # 2. final & confidenceが来るまで繰り返し
    #         while True:
    #             self.motion_gen.play_motion("nod_slight")
    #             received_data = self._receive(1024)
    #             received_count += 1
    #             try:
    #                 received = received_data.decode("utf-8")
    #             except UnicodeDecodeError:
    #                 received = "failed:\n"
    #             # 到着したlineを順番に見る
    #             #   複数行ある場合はfinalを再優先して取得＆confidenceが来たらbreak
    #             received_lines = received.splitlines()
    #             result = {}
    #             # print("received lines:: ", received_lines)
    #             for received_line in received_lines:
    #                 if received_line.startswith("startrecog:"):
    #                     result = {"type": "start", "user_utterance": "", "confidence": -1}
    #                 elif received_line.startswith("interimresult:"):
    #                     result = {"type": "interim", "user_utterance": received_line.lstrip("interimresult:"), "confidence": -1}
    #                 elif received_line.startswith("result:"):
    #                     result = {"type": "final", "user_utterance": received_line.lstrip("result:"), "confidence": -1}
    #                 elif received_line.startswith("confidence:"):
    #                     # confidenceが到着したら終了
    #                     if "type" in result and result["type"] == "final":
    #                         result["confidence"] = float(received_line.lstrip("confidence:"))
    #                 elif received_line.startswith("failed:"):
    #                     result = {"type": "failed", "user_utterance": "", "confidence": -1}
    #                 else:
    #                     # result = {"type": "failed", "user_utterance": "", "confidence": -1}
    #                     # break
    #                     raise Exception("{} is undefined result type.".format(received_line))
    #             self.received_stack.append(result)
    #             if result["type"] in ["failed", "final"]:
    #                 break

    #     except socket.timeout:
    #         self.received_stack.append( {"type": "silent", "user_utterance": "", "confidence": -1} )

    #     # 3. サーバを停止
    #     self.stop_listen()

    # def listen_once(self, silent_interval=3):
    #     self._settimeout(silent_interval)
    #     self.listener_thread = Thread(target=self.listener)
    #     self.listener_thread.start()

    # def listen_once_result_only(self):
    #     """
    #     1回だけASRに問い合わせる
    #     resultが来たら終了
    #     """

    #     # 1. サーバー起動
    #     self.start_listen()

    #     # 2. resultが来るまで待つ
    #     usr_utt, confidence = "", float()
    #     while True:
    #         received_str = ""
    #         received_data = self._receive(1024)

    #         if received_data:
    #             try:
    #                 received_str = received_data.decode("utf-8")
    #             except UnicodeDecodeError:
    #                 received_str = "result:failed\nconfidence:1\n"
    #             # print("GSRClient:: Received: {}".format(received_str))
    #         else:
    #             time.sleep(0.1)
    #             continue
            
    #         if received_str.startswith("result:"):
    #             # resultを受け取る
    #             result_str, confidence_str, _ = received_str.split("\n")
    #             usr_utt = result_str.lstrip("result:")
    #             confidence = float(confidence_str.lstrip("confidence:"))
    #             # 終了
    #             break
        
    #     # 3. サーバを停止
    #     self.stop_listen()
    #     # 4. asr_resultとして返還
    #     return deepcopy({"user_utterance": usr_utt, "confidence": confidence})
    
    # def recognize_speach(self):
    #     self.listen_once()
    #     while True:
    #         if not self.received_stack:
    #             time.sleep(0.1)
    #             continue
    #         result = self.received_stack.pop(0)
            
    #         if result["type"] in ["silent", "final", "failed"]:
    #             break
    #     print(str(result["user_utterance"]))
    #     return result["user_utterance"]
    
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
                        if time.time() - start_time > 1.5:  # n秒以上経過したか確認
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
            return User_res_text

        elif self.DIALOG_MODE == "console_dialog":
            usr_input_text = str(input("User> "))
            return usr_input_text
    
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
