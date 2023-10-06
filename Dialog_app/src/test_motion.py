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


print("深く頭を下げる挨拶の動作")
print(1)
motion_gen.play_motion("greeting_deep_head")
time.sleep(4)
print("============")

# 首を深く下げる挨拶の動作
print("首を深く下げる挨拶の動作")
print(1)
motion_gen.play_motion("greeting_deep_neck")
time.sleep(4)
print("============")

# 背骨を深く曲げる挨拶の動作
print("背骨を深く曲げる挨拶の動作")
print(1)
motion_gen.play_motion("greeting_deep_spine")
time.sleep(4)
print("============")

# 頭を軽く下げる挨拶の動作
print("頭を軽く下げる挨拶の動作")
print(1)
motion_gen.play_motion("greeting_head")
time.sleep(4)
print("============")

# 軽く頭を下げる挨拶の動作
print("軽く頭を下げる挨拶の動作")
print(1)
motion_gen.play_motion("greeting_light_head")
time.sleep(4)
print("============")

# 軽く首を下げる挨拶の動作
print("軽く首を下げる挨拶の動作")
print(1)
motion_gen.play_motion("greeting_light_neck")
time.sleep(4)
print("============")

# 背骨を軽く曲げる挨拶の動作
print("背骨を軽く曲げる挨拶の動作")
print(1)
motion_gen.play_motion("greeting_light_spine")
time.sleep(4)
print("============")

# 首を下げる挨拶の動作
print("首を下げる挨拶の動作")
print(1)
motion_gen.play_motion("greeting_neck")
time.sleep(4)
print("============")

# 背骨を曲げる挨拶の動作
print("背骨を曲げる挨拶の動作")
print(1)
motion_gen.play_motion("greeting_spine")
time.sleep(4)
print("============")

# 頭を左右にロールする動作
print("頭を左右にロールする動作")
print(1)
motion_gen.play_motion("head_roll_roll")
time.sleep(4)
print("============")

# 左の肩を伸ばす動作
print("左の肩を伸ばす動作")
print(1)
motion_gen.play_motion("leftshoulder_stretch")
time.sleep(4)
print("============")

# うなずく動作
print("うなずく動作")
print(1)
motion_gen.play_motion("nod")
time.sleep(4)
print("============")

# 頭を深くうなずく動作
print("頭を深くうなずく動作")
print(1)
motion_gen.play_motion("nod_deep_head")
time.sleep(4)
print("============")

# 軽くうなずく動作
print("軽くうなずく動作")
print(1)
motion_gen.play_motion("nod_slight")
time.sleep(4)
print("============")

# 頭を左右に振る「いいえ」の動作
print("頭を左右に振る「いいえ」の動作")
print(1)
motion_gen.play_motion("nono")
time.sleep(4)
print("============")

# 右の肩を伸ばす動作
print("右の肩を伸ばす動作")
print(1)
motion_gen.play_motion("rightshoulder_stretch")
time.sleep(4)
print("============")

# 両方の肩を伸ばす動作
print("両方の肩を伸ばす動作")
print(1)
motion_gen.play_motion("shoulder_stretch")
time.sleep(4)
print("============")

# 目を大きく開けて深く挨拶する動作
print("目を大きく開けて深く挨拶する動作")
print(1)
motion_gen.play_motion("greeting_deep_eye")
time.sleep(4)
print("============")

# 目を開けて挨拶する動作
print("目を開けて挨拶する動作")
print(1)
motion_gen.play_motion("greeting_eye")
time.sleep(4)
print("============")

# 目を大きく開けて深くうなずく動作
print("目を大きく開けて深くうなずく動作")
print(1)
motion_gen.play_motion("nod_deep_eye")
time.sleep(4)
print("============")

# 一般的な挨拶の動作
print("一般的な挨拶の動作")
print(1)
motion_gen.play_motion("greeting")
time.sleep(4)
print("============")

# 深く挨拶する動作
print("深く挨拶する動作")
print(1)
motion_gen.play_motion("greeting_deep")
time.sleep(4)
print("============")

# 軽く挨拶する動作
print("軽く挨拶する動作")
print(1)
motion_gen.play_motion("greeting_light")
time.sleep(4)
print("============")

# 深くうなずく動作
print("深くうなずく動作")
print(1)
motion_gen.play_motion("nod_deep")
time.sleep(4)
print("============")

motion_gen.play_motion("InitialPosition")