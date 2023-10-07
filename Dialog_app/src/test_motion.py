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

motion_list = [
    "greeting_deep_head",
    "greeting_deep_neck",
    "greeting_deep_spine",
    "greeting_head",
    "greeting_light_head",
    "greeting_light_neck",
    "greeting_light_spine",
    "greeting_neck",
    "greeting_spine",
    "head_roll_roll",
    "leftshoulder_stretch",
    "nod",
    "nod_deep_head",
    "nod_slight",
    "nono",
    "rightshoulder_stretch",
    "shoulder_stretch",
    "greeting_deep_eye",
    "greeting_eye",
    "nod_deep_eye",
    "greeting",
    "greeting_deep",
    "greeting_light",
    "nod_deep",
]

print("====================================")
for motion_id in motion_list:
    print(f"motionID : {motion_id}")
    time.sleep(1)
    motion_gen.play_motion(motion_id)
    time.sleep(4)
    print("====================================")

motion_gen.play_motion("InitialPosition")