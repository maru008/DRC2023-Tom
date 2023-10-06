# motion_generation.py
import json
import random
from .base import Base


class MotionGeneration(Base):
    def __init__(self, DIALOG_MODE, ip, port):
        super().__init__(ip, int(port))
        self.DIALOG_MODE = DIALOG_MODE
        self.ip = ip
        self.preset_motions = ["right_hand_safety", "left_hand_safety", "righthandonknee", "lefthandonknee"]
        self.default_motion = "null"

    def play_motion(self, motion_id):
        if self.DIALOG_MODE == "console_dialog":
            return None
        else:
            print(f"moving:{motion_id}")
            command = "playmotion=" + motion_id
            self._send_command(command)
            return command

    def send_command(self,controller, parameters={}):
        command_json = {
            "id": controller,
            "motionTowardObject": parameters.get("motionTowardObject", ""),
            "targetMotionMode": parameters.get("targetMotionMode", 2),
            "targetPoint": parameters.get("targetPoint", {}),
            "translateSpeed": parameters.get("translateSpeed", 2.0),
            "tracking": True
        }
        command = controller + "=" + json.dumps(command_json)
        self._send_command(command)
        return command

    def set_by_parameter(self, parameter):
        controlled_list = []
        for ctrl_key, ctrl_param in parameter.items():
            if ctrl_key == "playmotion":
                command = self.play_motion(ctrl_param)
            elif ctrl_key in  ["EyeController", "HeadController"]:
                command = self.send_command(ctrl_key, ctrl_param)
            controlled_list.append(command)
        return controlled_list

    def reset_body(self):
        motion_parameter =  {
            "EyeController": {
                "targetPoint": {
                "x": 0,
                "y": 1.2,
                "z": 1.5
                }
            },
            "HeadController": {
                "targetPoint": {
                "x": 0,
                "y": 1.2,
                "z": 1.5
                }
            }
        }
        return {"controlled_motion": self.set_by_parameter(motion_parameter)}
    
    def control_at_random(self):
        motion_name = random.choice(self.preset_motions)
        return {"controlled_motion": self.play_motion(motion_name)}
    
    def move_max_right(self):
    # 目, 頭, 体を右方向に向けるためのパラメータ
        motion_parameter = {
            "EyeController": {
                "targetPoint": {
                    "x": 2.0,  # x軸方向に2.0m右に
                    "y": 1.2,  # y軸方向は変更なし
                    "z": 1.5   # z軸方向は変更なし
                }
            },
            "HeadController": {
                "targetPoint": {
                    "x": 2.0,
                    "y": 1.2,
                    "z": 1.5
                }
            },
            "BodyController": {
                "targetPoint": {
                    "x": 2.0,
                    "y": 1.2,
                    "z": 1.5
                }
            }
        }
        print("move_max_right")
        return {"controlled_motion": self.set_by_parameter(motion_parameter)}
