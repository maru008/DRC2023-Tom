# main.py
import os
import sys
from datetime import datetime
import json
import threading

from utils.config_reader import read_config
from utils.general_tool import SectionPrint
from utils.TCPserver import SocketConnection
from utils.Google_Route_Search import search_route
from utils.determine_shot import *

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
speech_gen.speech_generate("""こんにちは！旅行代理店ロボットのしょうこです．
                           今回お客様は京都への旅行を考えていると聞きました．
                           私との会話でお客さんに最適な観光地を見つけるお手伝いをします！
                           何か旅行で体験したいことなどを教えて下さい．よろしくお願いします．""")
user_input_log = [{"role": "system", "content":ChatGPT_prompt_text}]

user_input_ls = []
system_output_text = []

Dialog_turn_num = 0

while True:
    Dialog_turn_num+=1
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
    resulting_sight_id_mtx = []
    for combination in all_combinations:
        print("対象クエリ:",combination)
        condition_json = json.dumps(combination)
        sight_ids = Sightseeing_mongodb.get_sight_ids_by_multiple_conditions(condition_json)
        print("結果観光地数:",len(sight_ids))
        if len(sight_ids) > 2 and len(sight_ids) < 100:
            resulting_sight_id_mtx.append(sight_ids)
        print("-------------------------------")
    print(resulting_sight_id_mtx)
    #===================================================================================================
    # 次のフェーズへ行く基準
    diversityScore = 2
    if len(resulting_sight_id_mtx) >= diversityScore:
        break
    if Dialog_turn_num > 7:
        break
    if Dialog_turn_num % 4 == 0 and len(resulting_sight_id_mtx) < 2:
        response_text = change_subject(data_as_json)
        speech_gen.speech_generate(response_text)
        user_input_log = [{"role": "system", "content":ChatGPT_prompt_text}]
        user_input_log.append({"role": "assistant", "content":response_text})
        
speech_gen.speech_generate("ありがとうございます．今回の旅行がどういうものか，そしてあなたがどんな人かわかりました！それではプランを作成します．少しお待ちください．")
#===================================================================================================
# +++++++++++++++++++++++++++++++ 4つの観光地を説明する ++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================

#画面表示するものを送る
# sightID_ls = [80026003,80026022,80025993,80025990] #これは一例
print("select 4 spot")
if len(resulting_sight_id_mtx) <= 1 and len(resulting_sight_id_mtx[0])<4:
    sightID_ls = [80026003,80026022,80025993,80025990] 
else:
    sightID_ls = select4spot(resulting_sight_id_mtx)
print("選ばれたIDリスト：",sightID_ls)
#画像表示サーバにデータを送る============================================================================
view_spot_json = Sightseeing_mongodb.create_send_json(sightID_ls)
sight_view.send_data(view_spot_json)

#  観光地紹介用GPT============================================================================
SpotIntro_prompt_path = os.path.join(script_dir,"DialogModules/Prompts/Spot_intro.txt")
with open(SpotIntro_prompt_path, 'r', encoding='utf-8') as f:
    SpotIntroGPT_prompt_text = f.read()
# 非同期処理用の関数============================================================================
def speach_view_monitor(head_text,title):
    speach_text = head_text  + title + "の写真と地図です．"
    speech_gen.speech_generate(speach_text)
    return speach_text

def intro_spot(spotdesc_text):
    # global response_from_intro_spot
    response_text = RobotNLG.ChatGPT(spotdesc_text,SpotIntroGPT_prompt_text,[])
    # response_from_intro_spot = response_text
    return response_text

# 観光地の紹介を開始============================================================================
head_text_ls = ["まず左上は，","次に右上は，","その左下は，","最後に右下は，"]
now_screen_state = ""
sightTitle_ls = []
for i,sightID_i in enumerate(sightID_ls):
    title_i = Sightseeing_mongodb.get_title_by_sight_id(sightID_i)
    sightTitle_ls.append(title_i)
    spoken_text = speach_view_monitor(head_text_ls[i],title_i)
    now_screen_state += spoken_text
    #DBから説明文取得
    desc_i = Sightseeing_mongodb.get_summary_by_sight_id(sightID_i)
    response_from_intro_spot = intro_spot(desc_i)
    # thread1 = threading.Thread(target=speach_view_monitor, args=(head_text_ls[i], title_i))
    # thread2 = threading.Thread(target=intro_spot, args=(desc_i,))

    # # スレッドを開始
    # thread1.start()
    # thread2.start()

    # # ここで、両方のスレッドが終了するのを待ちます
    # thread1.join()
    # thread2.join()
    speech_gen.speech_generate(response_from_intro_spot)

#===================================================================================================
# +++++++++++++++++++++++++++++++ ２つの観光地を絞る ++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
speech_gen.speech_generate("これら４つの観光地から二つの観光地を選んでください，よろしくお願いします．")
#二つの観光地を選ぶ段階

title_id_json = dict(zip(sightID_ls, sightTitle_ls))
print(title_id_json)
choice_two_spot_prompt = f'''
    いま画面に4つの観光地が表示されています．
    状況は{now_screen_state}
    観光地と観光地IDの対応は以下のJSONで定義されています．
    {title_id_json}
    この時，ユーザの応答を考えて観光地IDを配列形式で出力して．
    余計な文言を書かず，配列のみで，
    もし文章からは判断できなければ
    []
    のように空の配列で出力して．
'''
while True:
    user_input_text = voice_recog.recognize()
    response_text = RobotNLG.GPT4(user_input_text,choice_two_spot_prompt,[])
    trg2spotid = eval(response_text)
    print("得られたIDのリスト：",trg2spotid)
    if len(trg2spotid) == 2:
        break
    elif len(trg2spotid) > 2:
        speach_text = "すみません,2つに絞ってください．もう一度お願いします．"
        speech_gen.speech_generate(speach_text)
    else:
        speach_text = "すみません,理解できませんでした．もう一度お願いします．"
        speech_gen.speech_generate(speach_text)
        
trg2spotTitle = [Sightseeing_mongodb.get_title_by_sight_id(sightID_i) for sightID_i in trg2spotid]
speech_gen.speech_generate(f"ありがとうございます．お客様が行きたいスポットは{trg2spotTitle[0]}と{trg2spotTitle[1]}ですね．")
speech_gen.speech_generate("それではそれにあった経路を今から調べます．少しお待ちください．")

#===================================================================================================
# +++++++++++++++++++++++++++++++ 経路作成 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
#ここまでで二つの観光地を決めることができたと仮定
#以下は例
# lat1, long1 = 35.062358211, 135.736914797
# lat2, long2 = 35.060411266, 135.75270778
lat1, long1 = Sightseeing_mongodb.get_coordinates_by_sight_id(trg2spotid[0])
lat2, long2 = Sightseeing_mongodb.get_coordinates_by_sight_id(trg2spotid[1])
print(lat1, long1)
print(lat2, long2)
mode = "driving"
res_data = search_route(lat1, long1, lat2, long2, config.get("API_Key","Google"), mode)
new_json_data = {
    "directions": []
}

# 必要な情報を取り出して新しいJSONデータに追加
for route in res_data["routes"]:
    for leg in route["legs"]:
        for step in leg["steps"]:
            direction = {
                "distance": step["distance"]["text"],
                "duration": step["duration"]["text"],
                "instructions": step["html_instructions"]
            }
            new_json_data["directions"].append(direction)

# 辞書をJSON文字列に変換
new_json_string = json.dumps(new_json_data, ensure_ascii=False, indent=4)
print(new_json_string)

route_search_prompt_path = os.path.join(script_dir,"DialogModules/Prompts/For_route_search.txt")
with open(route_search_prompt_path, 'r', encoding='utf-8') as f:
    # ファイルの内容を読み込む
    routeInfo_prompt_text = f.read()

response_text = RobotNLG.ChatGPT(str(new_json_string),routeInfo_prompt_text,[])

speech_gen.speech_generate(f"{trg2spotTitle[0]}から{trg2spotTitle[1]}への行き方は次の通りです．")
speech_gen.speech_generate(response_text)

#===================================================================================================
# +++++++++++++++++++++++++++++++ 終わりの挨拶 ++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================

speech_gen.speech_generate("以上で案内を終了します．")

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