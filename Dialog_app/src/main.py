# main.py
import os
import sys
from datetime import datetime


from utils.config_reader import read_config
from utils.general_tool import *
from utils.TCPserver import *

from ServerModules.speech_generation import SpeechGeneration
from ServerModules.voice_recognition import VoiceRecognition
# from ServerModules.expression_generation import ExpressionGeneration
# from ServerModules.motion_generation import MotionGeneration

from DialogModules.NLGModule import NLG 


from database.mongo_tools import MongoDB



##引数情報を取得
config = read_config()
IP = config.get("Server_Info","Server_ip")
user_input_val = sys.argv[1] if len(sys.argv) > 1 else 'n'

if user_input_val == "y":
    DIALOG_MODE = "console_dialog"
    SectionPrint("コンソール対話モード")
elif user_input_val == "n":
    DIALOG_MODE = "robot_dialog"
    SectionPrint("ロボット対話モード")


#===================================================================================================
# +++++++++++++++++++++++++++++++ データベース準備 +++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
mongodb = MongoDB('Dialog_system') #クラス呼び出し
unique_id = mongodb.get_unique_collection_name() #コレクション名の取得

#===================================================================================================
# +++++++++++++++++++++++++++++++ サーバ準備 +++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
speech_gen = SpeechGeneration(DIALOG_MODE,IP,config.get("Server_Info","SpeechGenerator_port"))
voice_recog = VoiceRecognition(DIALOG_MODE,IP,config.get("Server_Info","SpeechRecognition_port"))
# expression_gen = ExpressionGeneration(DIALOG_MODE,IP,)
# motion_gen = MotionGeneration(DIALOG_MODE,IP,)

#===================================================================================================
# +++++++++++++++++++++++++++++++ LLM準備 +++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
RobotNLG = NLG(config)
script_dir = os.path.dirname(os.path.realpath(__file__))
Dialog_prompt_path = os.path.join(script_dir,"DialogModules/Prompts/Dialog_staff.txt")
with open(Dialog_prompt_path, 'r', encoding='utf-8') as f:
    # ファイルの内容を読み込む
    ChatGPT_prompt_text = f.read()
    
#===================================================================================================
# +++++++++++++++++++++++++++++++ 対話開始 +++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================

while True:
    user_input_text = voice_recog.recognize()

    if user_input_text in ["終了","quit"]:
        break
    
    LLMresponse_text = RobotNLG.ChatGPT(user_input_text,ChatGPT_prompt_text,[])
    
    speech_gen.speech_generate(LLMresponse_text)
    send_data('nlu_server_app',12345,LLMresponse_text)
    mongodb.add_to_array(unique_id, 'user_input_text', user_input_text)
    mongodb.add_to_array(unique_id, 'robot_output_text', LLMresponse_text)

SectionPrint("対話ログ出力")
# 会話の終了後、全ての会話ログを表示
keys = ['_id', 'user_input_text',"robot_output_text"]
mongodb.print_all_tables(keys)