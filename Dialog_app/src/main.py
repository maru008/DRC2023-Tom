# main.py
import os
import sys
from datetime import datetime
import json

from utils.config_reader import read_config
from utils.general_tool import SectionPrint
from utils.TCPserver import SocketConnection

from ServerModules.speech_generation import SpeechGeneration
from ServerModules.voice_recognition import VoiceRecognition
from ServerModules.face_expression_generation import ExpressionGeneration
from ServerModules.motion_generation import MotionGeneration

from DialogModules.NLGModule import NLG 


from database.mongo_tools import MongoDB,check_db_exists


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
print("======================")
print("Connecting to Database")
Dialog_mongodb = MongoDB('DRC2023_Dialog_DB') #クラス呼び出し
unique_id = Dialog_mongodb.get_unique_collection_name() #コレクション名の取得
print("======================")
#観光地MongoDBの用意
if check_db_exists("Sightseeing_Spot_DB") == False:
    sys.exit("観光地データベースを用意してください")

#===================================================================================================
# +++++++++++++++++++++++++++++++ ロボットサーバ準備 +++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
speech_gen = SpeechGeneration(DIALOG_MODE,IP,config.get("Server_Info","SpeechGenerator_port"))
voice_recog = VoiceRecognition(DIALOG_MODE,IP,config.get("Server_Info","SpeechRecognition_port"))
face_gen = ExpressionGeneration(DIALOG_MODE,IP,config.get("Server_Info","RobotExpressionController_port"))
motion_gen = MotionGeneration(DIALOG_MODE,IP,config.get("Server_Info","RobotBodyController_port"))

#===================================================================================================
# +++++++++++++++++++++++++++++++ 自前サーバ準備 +++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
socket_conn = SocketConnection('localhost', 12345) 

#===================================================================================================
# +++++++++++++++++++++++++++++++ フロントLLM準備 +++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
print("======================")
print("Preparing Front LLM")
RobotNLG = NLG(config)
script_dir = os.path.dirname(os.path.realpath(__file__))
Dialog_prompt_path = os.path.join(script_dir,"DialogModules/Prompts/Dialog_staff.txt")
with open(Dialog_prompt_path, 'r', encoding='utf-8') as f:
    # ファイルの内容を読み込む
    ChatGPT_prompt_text = f.read()
print("======================")
#===================================================================================================
# +++++++++++++++++++++++++++++++ 対話開始 +++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
motion_gen.play_motion("greeting_deep")
speech_gen.speech_generate("旅行代理店ロボットです．なんでも聞いてください．")
user_input_log = [{"role": "system", "content":ChatGPT_prompt_text}]
recive_data_num = 0

while True:
    # 発話認識
    motion_gen.play_motion("nod_slight")
    user_input_text = voice_recog.recognize()
    
    motion_gen.play_motion("nod_slight")
    
    user_input_log.append({"role": "user", "content":user_input_text})
    
    if user_input_text in ["終了","quit",":q"]:
        break
    
    LLMresponse_text = RobotNLG.ChatGPT(user_input_text,ChatGPT_prompt_text,user_input_log)
    
    #発話指示
    speech_gen.speech_generate(LLMresponse_text)
    
    #NLUサーバに文字列を送り，JSONを受け入れる
    response_data = socket_conn.send_data(str([unique_id,user_input_text]))
    try:
        response_data = json.loads(response_data)
        recive_data_num += len(response_data.keys())
    except:
        pass
    #データベースサーバにIDと文字列を送る
    Dialog_mongodb.add_to_array(unique_id, 'user_input_text', user_input_text)

    
    user_input_log.append({"role": "assistant", "content":LLMresponse_text})
    
    Dialog_mongodb.add_to_array(unique_id, 'robot_output_text', LLMresponse_text)
    if recive_data_num > 10:
        break
    
speech_gen.speech_generate("ありがとうございます．今回の旅行がどういうものが，そしてあなたがどんな人かわかりました！それではプランを作成します．少しお待ちください．")

SectionPrint("対話ログ出力")
# # 会話の終了後、作成されたMongoDBのデータを出力
Dialog_mongodb.print_collection(str(unique_id))