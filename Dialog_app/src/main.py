# main.py
import os
import sys
from datetime import datetime
import json
import threading

from utils.config_reader import read_config
from utils.general_tool import SectionPrint
from utils.TCPserver import SocketConnection

from ServerModules.speech_generation import SpeechGeneration
from ServerModules.voice_recognition import VoiceRecognition
from ServerModules.face_expression_generation import ExpressionGeneration
from ServerModules.motion_generation import MotionGeneration

from DialogModules.NLGModule import NLG 


from database.mongodb_tools_Dialog import MongoDB,check_db_exists,SightseeingDBHandler,SightViewTCPServer


USE_GPT_API = True

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
    
#　システムチェックでAPIを使わないのためのコマンド
console_input = input("GPTのAPIを使いますか?(使わない場合おうむ返しになります)(y/n):")
if console_input == "n":
    USE_GPT_API = False

#===================================================================================================
# +++++++++++++++++++++++++++++++ データベース準備 ++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================

print("Connecting to Database...")
Dialog_mongodb = MongoDB('DRC2023_Dialog_DB') #クラス呼び出し
unique_id = Dialog_mongodb.get_unique_collection_name() #コレクション名の取得
Dialog_mongodb.insert_initial_data(unique_id) #初期データの追加

#観光地MongoDBの用意
if check_db_exists("Sightseeing_Spot_DB") == False:
    sys.exit("観光地データベースを用意してください")
Sightseeing_mongodb = SightseeingDBHandler("Sightseeing_Spot_DB")
#===================================================================================================
# +++++++++++++++++++++++++++++++ ロボットサーバ準備 ++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
speech_gen = SpeechGeneration(DIALOG_MODE,IP,config.get("Server_Info","SpeechGenerator_port"))
voice_recog = VoiceRecognition(DIALOG_MODE,IP,config.get("Server_Info","SpeechRecognition_port"))
face_gen = ExpressionGeneration(DIALOG_MODE,IP,config.get("Server_Info","RobotExpressionController_port"))
motion_gen = MotionGeneration(DIALOG_MODE,IP,config.get("Server_Info","RobotBodyController_port"))
sight_view = SightViewTCPServer(IP,config.get("Server_Info","SiteViewer_port"))
#===================================================================================================
# +++++++++++++++++++++++++++++++ 自前サーバ準備 +++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
socket_conn = SocketConnection('localhost', 12345) 

#===================================================================================================
# +++++++++++++++++++++++++++++++ フロントLLM準備 ++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
print("Preparing Front LLM...")
RobotNLG = NLG(config)
script_dir = os.path.dirname(os.path.realpath(__file__))
Dialog_prompt_path = os.path.join(script_dir,"DialogModules/Prompts/Dialog_staff.txt")
with open(Dialog_prompt_path, 'r', encoding='utf-8') as f:
    # ファイルの内容を読み込む
    ChatGPT_prompt_text = f.read()
#===================================================================================================
# +++++++++++++++++++++++++++++++ 非同期処理用 ++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
def async_speech_generate(text):
    speech_gen.speech_generate(text)
    
def async_send_data(data):
    socket_conn.send_data(data)


Dialog_mongodb.print_collection_data(unique_id)
#===================================================================================================
# +++++++++++++++++++++++++++++++ 対話開始 +++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
motion_gen.play_motion("greeting_deep")
speech_gen.speech_generate("旅行代理店ロボットです．なんでも聞いてください．")
user_input_log = [{"role": "system", "content":ChatGPT_prompt_text}]

user_input_ls = []
system_output_text = []


while True:
    # 発話認識
    motion_gen.play_motion("nod_slight")
    user_input_text = voice_recog.recognize()
    
    motion_gen.play_motion("nod_slight")
    
    user_input_log.append({"role": "user", "content":user_input_text})
    
    if user_input_text in ["終了","quit","q"]:
        break
    
    # GPTを使うかどうか
    if USE_GPT_API:
        response_text = RobotNLG.ChatGPT(user_input_text,ChatGPT_prompt_text,user_input_log)
    else:
        response_text = user_input_text+"ってなんですか？"
        
    #===================================================================================================
    # 非同期処理開始
    speech_thread = threading.Thread(target=async_speech_generate, args=(response_text,))#発話指示
    send_data_thread = threading.Thread(target=async_send_data, args=(str([unique_id, user_input_text]),))#NLUサーバに文字列を送る（DBへの追加は向こう側）
    
    speech_thread.start()
    send_data_thread.start()
    
    # 必要に応じて、後の処理で両方のスレッドが終了するのを待つ
    speech_thread.join()
    send_data_thread.join()    
    
    ## ユーザとロボットのテキスト追加
    user_input_ls.append(user_input_text)
    system_output_text.append(response_text)
    #===================================================================================================

    # LLM用の対話ログ追加
    user_input_log.append({"role": "assistant", "content":response_text})
    Dialog_mongodb.print_collection_data(unique_id)

    #観光地絞り込みを行う
    ## 対話DBから現状のJSONを獲得
    data_as_json = Dialog_mongodb.fetch_data_by_id(unique_id)
    print(data_as_json)
    
    trg_Genre = "LGenre"
    #観光地DBへ検索
    result_data = Sightseeing_mongodb.fetch_sight_ids(data_as_json,trg_Genre)
    
    print("----------")
    genre = []
    for genre_value, ids in result_data.items():
        print(f"{trg_Genre}: {genre_value}")
        print("ヒットした観光地の数: ", len(ids))
        genre.append(genre_value)
        print("----------")
    total_genre = len(set((genre_value)))
    print(total_genre)
    if total_genre > 2:
        break
    

        
        
speech_gen.speech_generate("ありがとうございます．今回の旅行がどういうものか，そしてあなたがどんな人かわかりました！それではプランを作成します．少しお待ちください．")

#画面表示するものを送る
sightID_ls = [80026003,80026022,80025993,80025990] #これは一例
view_spot_json = Sightseeing_mongodb.create_send_json(sightID_ls)
sight_view.send_data(view_spot_json)


##  対話ログを追加
user_text_json = {
    "User_text":user_input_ls
}
system_text_json = {
    "System_text":system_output_text
}

Dialog_mongodb.update_data(unique_id,user_text_json)
Dialog_mongodb.update_data(unique_id,system_text_json)

SectionPrint("NLU結果出力")
# # 会話の終了後、作成されたMongoDBのデータを出力
Dialog_mongodb.print_collection_data(unique_id)