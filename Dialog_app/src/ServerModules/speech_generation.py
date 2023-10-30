import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
dialog_modules_dir = os.path.join(current_dir, '..', 'DialogModules')
sys.path.append(dialog_modules_dir)
from .base import Base
import socket
from copy import deepcopy
import json
import traceback
from DialogModules.Add_Hesitation import add_hesitation

class SpeechGeneration(Base):
    def __init__(self, DIALOG_MODE,ADD_HESITATION,ip, port):
        super().__init__(DIALOG_MODE,ip, int(port))

        self.config = {
            "engine": "POLLY-SSML",
            "speaker": "Mizuki",
            "duration-information":False,
            "speechmark":False,
            "text": ""
        }
        self.ssml_option = [
            ["<speak>", "</speak>"],
            ["<amazon:effect phonation='soft' vocal-tract-length='-15%'>","</amazon:effect>"],
            ["<prosody pitch='+0%' rate='105%' volume='medium'>", "</prosody>"]
        ]

    def _check_result(self, received_data):
        if "result" not in received_data:
            return ""

        elif received_data["result"] == "success-start":
            return ""

        if received_data["result"] == "success-end":
            print("{}:: End speaking successfully.".format(self.__class__.__name__))
            return "success-end"

        elif received_data["result"] == "failed":
            print("{}:: Failed speaking.".format(self.__class__.__name__))
            return "failed"

        else:
            print("{}:: {} is not TTS result.".format(self.__class__.__name__, received_data["result"]))
            return ""

    def _wait_speaking(self):
        print("{}:: Is speaking...".format(self.__class__.__name__))
        is_speaking = True
        while is_speaking:
            received = self.sock.recv(1024)
            try:
                received_data = json.loads(received.decode("utf-8").strip())
                result = self._check_result(received_data)
                if result in ["success-end", "failed"]:
                    break
            except:
                traceback.print_exc()
                sys.exit()
                time.sleep(0.1)
                continue
        return "success-end"

    def speech_generate(self, sentence, volume=""):
        print("{}:: Play one sentence.".format(self.__class__.__name__))
        print("System>",sentence)
        # 1. 送信データ作成
        ssml_text = sentence
        for head, tail in self.ssml_option[::-1]:
            if "medium" in head and volume:
                head = head.replace("medium", volume)
            ssml_text = head + ssml_text + tail
        command_dict = self.config.copy()
        command_dict.update({
            "text": ssml_text
        })
        command = json.dumps(command_dict)

        # 結果によっては追加で2回までやり直し
        failed_count = 0
        for _ in range(3):
            # 2. 送信
            self._send_command(command)

            # 3. 再生+インターバル待ち
            result = self._wait_speaking()

            if result == "success-end":
                break
            elif result == "failed":
                failed_count += 1
                continue

        return deepcopy({"result": result, "failed_count": failed_count})

    def print_one_sentence(self, sentence):
        # print("{}:: Print one sentence.".format(self.__class__.__name__))
        print("{}:: {}".format(self.__class__.__name__, sentence))

    # def __init__(self, , ip, port):
    #     self.DIALOG_MODE = DIALOG_MODE
    #     self.ADD_HESITATION = ADD_HESITATION
    #     self.ip = ip
    #     self.port = int(port)
    # def _send_command(self, command):
    #     command_ln = command + "\n"
    #     self.sock.send(command_ln.encode('utf-8'))

    # def speech_generate(self, text):
    #     print("System> ",text)
    #     if self.DIALOG_MODE == "robot_dialog":
    #         if self.ADD_HESITATION:
    #             #いい淀み付与コードの実行
    #             text = add_hesitation(text).replace("$", "<break time=\"0.2s\"/>").replace(":", "ーー。")
    #         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         try:
    #             self.sock.connect((self.ip, self.port))
                
    #             command_dict = {
    #                 "engine": "POLLY-SSML",
    #                 "speaker": "Mizuki",
    #                 "duration-information": False,
    #                 "speechmark": False,
    #                 "text": "<speak>" + text + "</speak>"
    #             }
    #             command = json.dumps(command_dict)
    #             self._send_command(command)

    #             buffer = ""
    #             while True:
    #                 received = self.sock.recv(1024)
    #                 buffer += received.decode("utf-8")
    #                 while '\n' in buffer:
    #                     message, buffer = buffer.split('\n', 1)
    #                     received_data = json.loads(message.strip())
    #                     if "result" in received_data:
    #                         if received_data["result"] == "success-end":
                                
    #                             print("SpeechGeneration: End speaking successfully.")
    #                             return
    #                         elif received_data["result"] == "failed":
    #                             print("SpeechGeneration: Failed speaking.")
    #                             return
    #         except Exception as e:
    #             print(f"SpeechGeneration: An error occurred: {e}")
    #             traceback.print_exc()
    #         finally:
    #             self.sock.close()
    #     elif self.DIALOG_MODE == "console_dialog":
    #         pass
