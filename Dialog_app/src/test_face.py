#　ロボット動作の動作テストコードです．
# 実行はpython src/test_face.pyで行う


import sys
from datetime import datetime
import json
import time

from utils.config_reader import read_config
from utils.general_tool import SectionPrint
from utils.TCPserver import SocketConnection

from ServerModules.speech_generation import SpeechGeneration
from ServerModules.voice_recognition import VoiceRecognition
from ServerModules.face_expression_generation import ExpressionGeneration
from ServerModules.motion_generation import MotionGeneration

from DialogModules.NLGModule import NLG 


from Dialog_app.src.database.mongodb_tools_Dialog import MongoDB


config = read_config()
IP = config.get("Server_Info","Server_ip")

user_input_val = input("コマンド対話モードを実行しますか (y/n)?")
if user_input_val == "y":
    DIALOG_MODE = "console_dialog"
    SectionPrint("コンソール対話モード")
elif user_input_val == "n":
    DIALOG_MODE = "robot_dialog"
    SectionPrint("ロボット対話モード")
else:
    sys.exit('正しく入力してください')

face_gen = ExpressionGeneration(DIALOG_MODE,IP,config.get("Server_Info","RobotExpressionController_port"))

face_gen.set_expression("fullsmile")
time.sleep(4)
face_gen.set_expression("bad")
time.sleep(4)
face_gen.set_expression("angry")
time.sleep(4)
face_gen.reset_expression()