# speech_generation.py
class SpeechGeneration:
    def __init__(self,DIALOG_MODE, ip, port):
        self.DIALOG_MODE =DIALOG_MODE
        self.ip = ip
        self.port = port
   
    def speech_generate(self, text):
        if self.DIALOG_MODE == "robot_dialog":
            print(self.ip,self.port)
            pass
            #ここにサーバに接続するコードを書く
        elif self.DIALOG_MODE == "console_dialog":
            print(f"robot:{text}ってなんですか")