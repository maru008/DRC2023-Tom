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
from ServerModules.sight_view import SightViewTCPServer

from DialogModules.NLGModule import NLG 


from database.mongodb_tools_Dialog import MongoDB,check_db_exists
from database.mongodb_tools_Sightseeing import SightseeingDBHandler,generate_combinations


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
# +++++++++++++++++++++++++++++++ 対話開始 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
motion_gen.play_motion("greeting_deep")
speech_gen.speech_generate("こんにちは！旅行代理店ロボットです．なんでも聞いてください．")
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
    
    #===================================================================================================
    # 現状のNLUの結果を出力
    Dialog_mongodb.print_collection_data(unique_id)
    #===================================================================================================
    #観光地絞り込みを行う
    ## 対話DBから現状のJSONを獲得
    data_as_json = Dialog_mongodb.fetch_data_by_id(unique_id)
    #基準とするコードの作成
    #観光地DBへ検索
    all_combinations = generate_combinations(data_as_json)
    resulting_sight_ids = set()
    for combination in all_combinations:
        print("対象クエリ:",combination)
        condition_json = json.dumps(combination)
        sight_ids = Sightseeing_mongodb.get_sight_ids_by_multiple_conditions(condition_json)
        print("結果観光地数:",len(sight_ids))
        resulting_sight_ids.update(sight_ids)
    print(list(resulting_sight_ids))
    #===================================================================================================
    # 次のフェーズへ行く基準
        
speech_gen.speech_generate("ありがとうございます．今回の旅行がどういうものか，そしてあなたがどんな人かわかりました！それではプランを作成します．少しお待ちください．")
#===================================================================================================
# +++++++++++++++++++++++++++++++ 2つの観光地を絞り込む ++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
print(trg_id_mtx)
#画面表示するものを送る
# sightID_ls = [80026003,80026022,80025993,80025990] #これは一例

sightID_ls = [trg_id_mtx[0][0],trg_id_mtx[0][1],trg_id_mtx[1][0],trg_id_mtx[1][1]] #これも一例
view_spot_json = Sightseeing_mongodb.create_send_json(sightID_ls)
sight_view.send_data(view_spot_json)

text_sight1_title = f"まずは左上が{Sightseeing_mongodb.get_title_by_sight_id(trg_id_mtx[0][0])}です．"

speech_gen.speech_generate(text_sight1_title)

text_sight1_summary = Sightseeing_mongodb.get_summary_by_sight_id(trg_id_mtx[0][0])
speech_gen.speech_generate(text_sight1_summary)

text_sight1_title = f"そして右上が{Sightseeing_mongodb.get_title_by_sight_id(trg_id_mtx[0][1])}です．"

speech_gen.speech_generate(text_sight1_title)
text_sight1_summary = Sightseeing_mongodb.get_summary_by_sight_id(trg_id_mtx[0][1])
speech_gen.speech_generate(text_sight1_summary)

text_sight1_title = f"さらに左下が{Sightseeing_mongodb.get_title_by_sight_id(trg_id_mtx[1][0])}です．"

speech_gen.speech_generate(text_sight1_title)
text_sight1_summary = Sightseeing_mongodb.get_summary_by_sight_id(trg_id_mtx[1][0])
speech_gen.speech_generate(text_sight1_summary)

text_sight1_title = f"最後に右下が{Sightseeing_mongodb.get_title_by_sight_id(trg_id_mtx[1][1])}です．"

speech_gen.speech_generate(text_sight1_title)
text_sight1_summary = Sightseeing_mongodb.get_summary_by_sight_id(trg_id_mtx[1][1])
speech_gen.speech_generate(text_sight1_summary)







#===================================================================================================
# +++++++++++++++++++++++++++++++ 経路作成 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
#ここまでで二つの観光地を決めることができたと仮定
#以下は例
lat1, long1 = 35.062358211, 135.736914797
lat2, long2 = 35.060411266, 135.75270778




#===================================================================================================
# +++++++++++++++++++++++++++++++ 会話終了後の処理 ++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================

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