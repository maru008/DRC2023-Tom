# main.py
import os
import sys
from datetime import datetime


from utils.config_reader import read_config
from utils.general_tool import SectionPrint
from utils.TCPserver import SocketConnection

from ServerModules.speech_generation import SpeechGeneration
from ServerModules.voice_recognition import VoiceRecognition
# from ServerModules.expression_generation import ExpressionGeneration
# from ServerModules.motion_generation import MotionGeneration

from DialogModules.NLGModule import NLG 


from database.mongo_tools import MongoDB


##引数情報を取得
config = read_config()
IP = config.get("Server_Info","Server_ip")
user_input_val = sys.argv[1]
if user_input_val == "y":
    DIALOG_MODE = "console_dialog"
    SectionPrint("コンソール対話モード")
elif user_input_val == "n":
    DIALOG_MODE = "robot_dialog"
    SectionPrint("ロボット対話モード")
else:
    sys.exit('正しく入力してください')
    


#===================================================================================================
# +++++++++++++++++++++++++++++++ データベース準備 +++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
mongodb = MongoDB('Dialog_system') #クラス呼び出し
unique_id = mongodb.get_unique_collection_name() #コレクション名の取得

#===================================================================================================
# +++++++++++++++++++++++++++++++ ロボットサーバ準備 +++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
speech_gen = SpeechGeneration(DIALOG_MODE,IP,config.get("Server_Info","SpeechGenerator_port"))
voice_recog = VoiceRecognition(DIALOG_MODE,IP,config.get("Server_Info","SpeechRecognition_port"))
# expression_gen = ExpressionGeneration(DIALOG_MODE,IP,)
# motion_gen = MotionGeneration(DIALOG_MODE,IP,)

#===================================================================================================
# +++++++++++++++++++++++++++++++ 自前サーバ準備 +++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
socket_conn = SocketConnection('localhost', 12345) 

#===================================================================================================
# +++++++++++++++++++++++++++++++ フロントLLM準備 +++++++++++++++++++++++++++++++++++++++++++++++
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
speech_gen.speech_generate("こんにちは，旅行代理店ロボットのしょうこです．なんでも聞いてください．")
user_input_log = [{"role": "system", "content":ChatGPT_prompt_text}]

while True:
    # print(f"{dilognum}:音声認識開始")
    user_input_text = voice_recog.recognize()
    # print(f"{dilognum}:音声認識終了")
    user_input_log.append({"role": "user", "content":user_input_text})
    if user_input_text in ["終了","quit",":q"]:
        break
    #バックエンドサーバに送る
    socket_conn.send_data(user_input_text)
    mongodb.add_to_array(unique_id, 'user_input_text', user_input_text)
    
    # LLMresponse_text = RobotNLG.ChatGPT(user_input_text,ChatGPT_prompt_text,user_input_log)
    LLMresponse_text = RobotNLG.GPT4(user_input_text,ChatGPT_prompt_text,user_input_log)
    user_input_log.append({"role": "assistant", "content":LLMresponse_text})
    
    
    speech_gen.speech_generate(LLMresponse_text)
    
    
    
    mongodb.add_to_array(unique_id, 'robot_output_text', LLMresponse_text)
    
    
SectionPrint("対話ログ出力")
# 会話の終了後、全ての会話ログを表示
keys = ['_id', 'user_input_text',"robot_output_text"]
mongodb.print_all_tables(keys)