#　顔表情の動作テストコードです．
# 実行はpython src/test_motion.pyで行う


import sys
from datetime import datetime

import time

from utils.config_reader import read_config
from utils.general_tool import SectionPrint

from ServerModules.motion_generation import MotionGeneration

from DialogModules.NLGModule import NLG 


from database.mongo_tools import MongoDB

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

motion_gen = MotionGeneration(DIALOG_MODE,IP,config.get("Server_Info","RobotBodyController_port"))


motion_gen.play_motion("right_hand_safety")
time.sleep(4)
motion_gen.play_motion("left_hand_safety")
time.sleep(4)
motion_gen.play_motion("righthandonknee")
time.sleep(4)
motion_gen.play_motion("lefthandonknee")
time.sleep(4)

motion_gen.play_motion("lefthandonknee")
motion_gen.play_motion("righthandonknee")
time.sleep(4)
motion_gen.reset_body()

