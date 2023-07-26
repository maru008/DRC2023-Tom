# voice_recognition.py
class VoiceRecognition:
    def __init__(self,DIALOG_MODE, ip, port):
        self.DIALOG_MODE =DIALOG_MODE
        self.ip = ip
        self.port = port
    
    def recognize(self):
        if self.DIALOG_MODE == "robot_dialog":
            usr_input_text = str(input("user:"))
            return usr_input_text
            #ここにサーバに接続するコードを書く
        elif self.DIALOG_MODE == "console_dialog":
            usr_input_text = str(input("user:"))
            return usr_input_text
            
        
