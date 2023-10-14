#　顔表情の動作テストコードです．
# 実行はpython src/test_motion.pyで行う


import sys
from datetime import datetime

import time

from utils.config_reader import read_config
from utils.general_tool import SectionPrint

from ServerModules.motion_generation import MotionGeneration

from DialogModules.NLGModule import NLG 

config = read_config()
IP = config.get("Server_Info","Server_ip")
DIALOG_MODE = "robot_dialog"


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

# print("====================================")
# for motion_id in motion_list[0:2]:
#     print(f"motionID : {motion_id}")
#     time.sleep(1)
#     motion_gen.play_motion(motion_id)
#     time.sleep(4)
#     print("====================================")

# motion_gen.play_motion("InitialPosition")

motion_gen.move_max_right()
time.sleep(4)
motion_gen.reset_body()