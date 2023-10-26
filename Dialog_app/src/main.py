# main.py
import os
import sys
import datetime
import re
import time
import queue
import json
import threading

from utils.config_reader import read_config
from utils.general_tool import SectionPrint,check_time_exceeded
from utils.TCPserver import SocketConnection
from utils.NAVITIME_Route_serach import NAVITME
from utils.determine_shot import change_subject,select4spot
from utils.judge_break import Judge_roop_break,Judge_change_subject

from ServerModules.speech_generation import SpeechGeneration
from ServerModules.voice_recognition import VoiceRecognition
from ServerModules.face_expression_generation import ExpressionGeneration
from ServerModules.motion_generation import MotionGeneration
from ServerModules.sight_view import SightViewTCPServer
from ServerModules.tcp_server import ConversationSignalHandler

from DialogModules.NLGModule import NLG 

from database.mongodb_tools_Dialog import MongoDB,check_db_exists
from database.mongodb_tools_Sightseeing import SightseeingDBHandler,generate_combinations


USE_GPT_API = True
ADD_HESITATION = False
#===================================================================================================
# +++++++++++++++++++++++++++++++ 各種パラメタ設定準備 ++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
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

# console_input = input("GPTのAPIを使いますか?(使わない場合おうむ返しになります)(y/n):")
# console_input = "y"
# if console_input == "n":
#     USE_GPT_API = False
# console_input = input("いい淀みを付与しますか？:(y/n)")
# if console_input == "y":
#     ADD_HESITATION = True

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
speech_gen = SpeechGeneration(DIALOG_MODE,ADD_HESITATION,IP,config.get("Server_Info","SpeechGenerator_port"))
voice_recog = VoiceRecognition(DIALOG_MODE,IP,config.get("Server_Info","SpeechRecognition_port"))
face_gen = ExpressionGeneration(DIALOG_MODE,IP,config.get("Server_Info","RobotExpressionController_port"))
motion_gen = MotionGeneration(DIALOG_MODE,IP,config.get("Server_Info","RobotBodyController_port"))
sight_view = SightViewTCPServer(DIALOG_MODE,IP,config.get("Server_Info","SiteViewer_port"))
TCP_server = ConversationSignalHandler(DIALOG_MODE,IP,config.get("Server_Info","TCPServer_port"))
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
    ChatGPT_prompt_text = f.read()
## 逐次生成のための間数
# def yield_speech_message(generator_function, user_input_text, ChatGPT_prompt_text, user_input_log):
#     speach_t = ""
#     for talk in generator_function(user_input_text, ChatGPT_prompt_text, past_messages=user_input_log):
#         speach_t += talk
#         if "。" in speach_t or "！" in speach_t:
#             speech_gen.speech_generate(speach_t)
#             speach_t = ""
#     return speach_t

def yield_speech_message(generator_function, user_input_text, ChatGPT_prompt_text, user_input_log):
    global stop_generation
    speach_t = ""
    sentence_count = 0
    for talk in generator_function(user_input_text, ChatGPT_prompt_text, past_messages=user_input_log):
        speach_t += talk
        if "。" in talk or "！" in talk or "？" in talk:
            sentence_count +=1
            if sentence_count == 1 and len(speach_t) < 15:#短い一文ならpass
                pass
            else:
                response_queue.put(speach_t) 
                speach_t = ""
    stop_generation = True

#===================================================================================================
# +++++++++++++++++++++++++++++++ 非同期処理用関数 +++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================


# def async_speech_generate(user_input_text,ChatGPT_prompt_text,user_input_log):
#     global response_text
#     response_text = yield_speech_message(RobotNLG.yield_GPT4_message, user_input_text, ChatGPT_prompt_text, user_input_log)

def async_send_data(data):
    socket_conn.send_data(data)

def async_speech_generate():
    global response_queue
    global response_text
    while not stop_generation or not response_queue.empty():  # stop_generationがTrueかつキューが空になったらループを終了
        if not response_queue.empty():
            response_text = response_queue.get()
            speech_gen.speech_generate(response_text)
            # time.sleep(1)

#===================================================================================================
# +++++++++++++++++++++++++++++++ 対話開始 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
#  ユーザとシステムのログを記録
user_input_text_ls = []
system_output_text_ls = []
resulting_sight_id_mtx = []

#TCP開始サーバ接続------------------------------------------------------------------------------------
#最初の時間を記録

print("Send start command ...")
TCP_server.connect_and_request_rule()
print("Conversation start signal waiting ...")
TCP_server.check_start_signal()
TCP_server.close()
print("Conversation started!")
SectionPrint("対話開始")
#対話開始-----------------------------------------------------------------------------------------------
start_time = datetime.datetime.now()
#お辞儀
motion_gen.play_motion("greeting_deep")
speach_t = """こんにちは！旅行代理店ロボットのしょうこです。今回お客様は京都への旅行を考えていると聞きました。私との会話でお客様に最適な観光地を見つけるお手伝いをします！何か旅行で体験したいことなどを教えて下さい。よろしくお願いします。"""
speech_gen.speech_generate(speach_t)
system_output_text_ls.append(speach_t)

user_input_log_firstContact = [{"role": "system", "content":ChatGPT_prompt_text}]

#進行を記録
Dialog_turn_num = 0
stop_generation = False
already_serach_json = []
while True:
    # 対話状態更新
    Dialog_turn_num += 1
    current_time = datetime.datetime.now()
    #ブレークジャッジ(Judge_break_boolがtureならループを抜ける)
    Judge_break_bool = Judge_roop_break(resulting_sight_id_mtx,Dialog_turn_num,start_time,current_time)
    #話題変換ジャッジ(Judge_change_subject_boolがtureなら話題を変換する)
    Judge_change_subject_bool = Judge_change_subject(resulting_sight_id_mtx,Dialog_turn_num)
    print(f"終了:{Judge_break_bool}, 話題変更:{Judge_change_subject_bool}")
    # 発話認識
    motion_gen.play_motion("nod_slight")
    user_input_text = voice_recog.recognize()
    motion_gen.play_motion("nod_slight")
    user_input_log_firstContact.append({"role": "user", "content":user_input_text})
    
    #===================================================================================================
    # 非同期処理開始
    response_queue = queue.Queue()
    speech_thread = threading.Thread(target=yield_speech_message, args=(RobotNLG.yield_GPT4_message, user_input_text, ChatGPT_prompt_text, user_input_log_firstContact))
    send_data_thread = threading.Thread(target=async_send_data, args=(str([unique_id, user_input_text]),))#NLUサーバに文字列を送る（DBへの追加は向こう側）
    
    speech_thread.start()
    send_data_thread.start()
    
    stop_generation = False
    async_speech_generate()
    
    speech_thread.join()
    send_data_thread.join()
    
    ## ユーザとロボットのテキスト追加
    user_input_text_ls.append(user_input_text)
    system_output_text_ls.append(response_text)
    #===================================================================================================
    # LLM用の対話ログ追加
    user_input_log_firstContact.append({"role": "assistant", "content":response_text})
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
    
    for combination in all_combinations:
        if str(combination) not in already_serach_json:
            condition_json = json.dumps(combination)
            sight_ids = Sightseeing_mongodb.get_sight_ids_by_multiple_conditions(condition_json)
            if len(sight_ids) >= 2 and len(sight_ids) < 100:
                print("対象クエリ:",combination)
                print("結果観光地数:",len(sight_ids))
                resulting_sight_id_mtx.append(sight_ids)
                print("-------------------------------")
            already_serach_json.append(str(combination))
    print(resulting_sight_id_mtx)
    #===================================================================================================
    # 次のフェーズへ行くかどうかの判定
    if Judge_break_bool:
        break
    else:
        # 話題変換をするかどうかの判定
        if Judge_change_subject_bool:
            response_text = change_subject(data_as_json)
            speech_gen.speech_generate(response_text)
            #chatgptのログを初期化（最大トークン数エラーを回避するため）
            user_input_log_firstContact = [{"role": "system", "content":ChatGPT_prompt_text}]
            user_input_log_firstContact.append({"role": "assistant", "content":response_text})
    # 時間表示
    print("---------------------------------")
    check_time_exceeded(start_time)

#===================================================================================================
# +++++++++++++++++++++++++++++++ 4つの観光地を説明する ++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
# 配列から4つを選ぶ----------------------------------------------------------------------------------------
Select4_Bool = False
print("select 4 spot...",end="")
sightID_ls = select4spot(resulting_sight_id_mtx)
print("selected->",sightID_ls)

if sightID_ls is None:
    sightID_ls = [80026003,80026022,80025993,80025990] #得られなかったら仮の4つ選ぶ
    result_user_json ={}
else:
    result_user_json = data_as_json
    Select4_Bool = True

sightTitle_ls = [Sightseeing_mongodb.get_title_by_sight_id(sightID_i) for sightID_i in sightID_ls]
print("選ばれた観光地リスト: ",sightTitle_ls)
# 3つ非同期処理関数定義========================================================================================
# ・thread1：表の発話や画面表示 async_speach_json_result -> 発話したり、画面表示したり
# ・thread2：推薦根拠の生成 async_generate_spot_reason -> spot_reason_textを作成
# ・thread3：観光地説明の要約生成 async_generate_spot_desc -> spot_desc_text_lsを更新
spot_desc_text_ls = []
now_screen_state = []
def async_speach_json_result(Select4_Bool,sightID_ls):
    speach_t ="ありがとうございます。今回の旅行がどういうものか、そしてあなたがどんな人かわかりました！それではいくつか観光地を検索いたします。少しお待ちください。"
    speech_gen.speech_generate(speach_t)
    system_output_text_ls.append(speach_t)
    if not Select4_Bool:
        speach_t = "申し訳ありません。お客様に合致した観光地を見つけることができませんでした。今回は京都で代表的な観光地を上げさせていただきます。"
        speech_gen.speech_generate(speach_t)
        system_output_text_ls.append(speach_t)
    view_spot_json = Sightseeing_mongodb.create_send_json(sightID_ls)
    sight_view.send_data(view_spot_json)
    speach_t = "こちらの画面に、今回お客様に推薦する4つの観光地を表示しています。これら4つの観光地から2つを選んでいただきます。"
    speech_gen.speech_generate(speach_t)
    system_output_text_ls.append(speach_t)
# ----------------------------------------------------------------------------------------------
def async_generate_spot_reason(sightTitle_ls,user_json):
    global spot_reason_text
    SpotReason_prompt_path = os.path.join(script_dir,"DialogModules/Prompts/Spot_reason.txt")
    with open(SpotReason_prompt_path, 'r', encoding='utf-8') as f:
        SpotReason_prompt_text = f.read()
    input_text = str(sightTitle_ls) + "\n" + json.dumps(user_json)
    spot_reason_text = RobotNLG.GPT4(input_text,SpotReason_prompt_text,[])
# ----------------------------------------------------------------------------------------------
SpotIntro_prompt_path = os.path.join(script_dir,"DialogModules/Prompts/Spot_intro.txt")
with open(SpotIntro_prompt_path, 'r', encoding='utf-8') as f:
    SpotIntroGPT_prompt_text = f.read()
def async_generate_spot_desc(sightID_ls,sightTitle_ls):
    global spot_desc_text_ls
    head_text_ls = ["まず左上は、","次に右上は、","その左下は、","最後に右下は、"]
    for i,sightID_i in enumerate(sightID_ls):
        print(f"creating {sightID_i} desc")
        viwe_spot_text = head_text_ls[i]  + sightTitle_ls[i] + "の写真と地図です。ご覧ください。"
        spot_desc_text_ls.append(viwe_spot_text)
        now_screen_state.append(viwe_spot_text)
        desc_i = Sightseeing_mongodb.get_summary_by_sight_id(sightID_i)
        spot_desc_text_ls.append(RobotNLG.GPT4(desc_i,SpotIntroGPT_prompt_text,[]))

sightDesc_ls = [Sightseeing_mongodb.get_summary_by_sight_id(sightID_i) for sightID_i in sightID_ls]

# 並列処理開始-------------------------------------------------------------------------------------
thread1 = threading.Thread(target=async_speach_json_result, args=(Select4_Bool,sightID_ls))
thread2 = threading.Thread(target=async_generate_spot_reason, args=(sightTitle_ls,result_user_json,))
thread3 = threading.Thread(target=async_generate_spot_desc, args=(sightID_ls,sightTitle_ls))
thread1.start()
thread2.start()
thread3.start()

thread1.join()
thread2.join()
check_time_exceeded(start_time)

#推薦理由の発話
speech_gen.speech_generate(spot_reason_text)
system_output_text_ls.append(spot_reason_text)

speach_t = "それでは、4つそれぞれについて説明させていただきます。"
speech_gen.speech_generate(speach_t)
system_output_text_ls.append(speach_t)
for desc_i in spot_desc_text_ls:
    speech_gen.speech_generate(desc_i)
    system_output_text_ls.append(desc_i)
    check_time_exceeded(start_time)
    
spot_desc_text_json = json.dumps(dict(zip(sightTitle_ls,sightDesc_ls)))
#===================================================================================================
# +++++++++++++++++++++++++++++++ ４つの観光地について質疑応答を受ける +++++++++++++++++++++++++++++++++++
#===================================================================================================
desc_4spot_prompt = f"""
    あなたは旅行代理店の接客のプロです。
    この度のお客様は京都市内の観光を目的としてご来店されました。
    
    今、4つの観光地で悩んでいます。
    4つのスポットは以下のJSON形式で書かれており，観光地とその説明が書かれています．
    {spot_desc_text_json}
    お客様がこれらの観光地について質問をしようとしているので，上のデータ基づいて適切に対応してください．．
    
    箇条書きや掛け合いの文書など発話としておかしな出力はしないでください．
    会話は１文程度で相手を圧倒しないようにしてください。
    
    もしお客さんが質問がないと発話していると判断したら最後に $break$ と出力してください．
"""
def contains_break_string(s):
    """
    質問がないかどうかを判定する間数
    """
    return bool(re.search(r'\$break\$', s))
speach_t = "以上が4つの観光地の説明です。何か質問あればなんでもお答えします．いかがでしょうか"
speech_gen.speech_generate(speach_t)

user_input_log_desc4spot = []
while True:
    user_input_text = voice_recog.recognize()
    user_input_log_desc4spot.append({"role": "user", "content":user_input_text})
    if check_time_exceeded(start_time,threshold_minutes=15):
        speach_t = "すみません，お時間が迫っているようなので先に進みます．"
        speech_gen.speech_generate(speach_t)
        break
    else:
        response_queue = queue.Queue()
        speech_thread = threading.Thread(target=yield_speech_message, args=(RobotNLG.yield_GPT4_message, user_input_text, desc_4spot_prompt, user_input_log_desc4spot))
        speech_thread.start()
        stop_generation = False
        async_speech_generate()
        if contains_break_string(response_text):
            break
        print(response_text)
        user_input_log_desc4spot.append({"role": "assistant", "content":response_text})
        
        

#===================================================================================================
# +++++++++++++++++++++++++++++++ ２つの観光地を絞る ++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
speech_gen.speech_generate("ありがとうございます。それではどの２つの観光地に行くかを選んでいただきたいです。よろしくお願いします。")

#二つの観光地を選ぶ段階---------------------------------------------------------------------------------
title_id_json = dict(zip(sightID_ls, sightTitle_ls))
choice_two_spot_prompt = f'''
        いま画面に4つの観光地が表示されています。
        状況は{now_screen_state}
        観光地と観光地IDの対応は以下のJSONで定義されています。
        {title_id_json}
        この時、ユーザの応答を考えて観光地IDを配列形式で出力して。
        余計な文言を書かず、配列のみで、
        もし文章からは判断できなければ
        []
        のように空の配列で出力して。
    '''
while True:
    user_input_text = voice_recog.recognize()
    user_input_text_ls.append(user_input_text)
    response_text = RobotNLG.GPT4(user_input_text,choice_two_spot_prompt,[])
    trg2spotid = eval(response_text)
    print("得られたIDのリスト：",trg2spotid)
    if len(trg2spotid) == 2:
        break
    elif len(trg2spotid) <= 1:
        speach_text = "すみません,2つを選んでください。もう一度お願いします。"
    elif len(trg2spotid) > 2:
        speach_text = "すみません,2つに絞ってください。もう一度お願いします。"
    else:
        speach_text = "すみません,理解できませんでした。もう一度お願いします。"
    speech_gen.speech_generate(speach_text)
    system_output_text_ls.append(speach_text)
    check_time_exceeded(start_time)

trg2spotTitle = [Sightseeing_mongodb.get_title_by_sight_id(sightID_i) for sightID_i in trg2spotid]

#行き先の追加
User_going_spot = {
    "User_going_spot":trg2spotTitle
}
Dialog_mongodb.update_data(unique_id,User_going_spot)
#===================================================================================================
# +++++++++++++++++++++++++++++++ 経路作成 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
lat1, long1 = Sightseeing_mongodb.get_coordinates_by_sight_id(trg2spotid[0])
lat2, long2 = Sightseeing_mongodb.get_coordinates_by_sight_id(trg2spotid[1])
NAVITME_serach = NAVITME(config,lat1, long1, lat2, long2)

#経路案内用プロンプト
route_search_prompt_path = os.path.join(script_dir,"DialogModules/Prompts/For_route_search.txt")
with open(route_search_prompt_path, 'r', encoding='utf-8') as f:
    # ファイルの内容を読み込む
    routeInfo_prompt_text = f.read()

def async_speach_spot(trg2spotTitle):
    speach_t = f"ありがとうございます。お客様が行きたいスポットは{trg2spotTitle[0]}と{trg2spotTitle[1]}ですね。"
    speech_gen.speech_generate(speach_t)
    speach_t = "それではこの店から出発し、公共交通機関で観光地を巡り、帰ってくるプランを検索いたします。少しお待ちください。"
    speech_gen.speech_generate(speach_t)

def async_search_route():
    global journey_ls
    journey_ls = NAVITME_serach.get_route_text(0)#この0は候補の番目
    print("NAVITIME> Serach route done!")

#並列処理--------------------------------------------------------------------------------------------
start_point, end_point = "JTBユニモール名古屋", "JTBユニモール名古屋"
print("-------------start multi-thread processing (speach and serach route)-------------")
thread1 = threading.Thread(target=async_speach_spot, args=(trg2spotTitle,))
thread2 = threading.Thread(target=async_search_route, args=())
# スレッドを開始
thread1.start()
thread2.start()
# ここで、両方のスレッドが終了するのを待ちます
thread1.join()
thread2.join()

route_info_json = {
        "start_end_spot":[start_point,end_point],
        "via_spot":trg2spotTitle,
        "route_desc":journey_ls,
}
past_messages = []
#経路について発話
response_queue = queue.Queue()
speech_thread = threading.Thread(target=yield_speech_message, args=(RobotNLG.yield_GPT4_message, user_input_text, desc_4spot_prompt, user_input_log_desc4spot))
speech_thread.start()

stop_generation = False
async_speech_generate()
# yield_speech_message(RobotNLG.yield_GPT4_message, str(route_info_json), routeInfo_prompt_text, past_messages)

## 対話ログを追加--------------------------------------------------------------------------------------------
# user_text_json = {
#     "User_text":user_input_text_ls
# }
# system_text_json = {
#     "System_text":system_output_text_ls
# }
# Dialog_mongodb.update_data(unique_id,user_text_json)
# Dialog_mongodb.update_data(unique_id,system_text_json)
#===================================================================================================
# +++++++++++++++++++++++++++++++ 根拠に基づく推薦事後対話 ++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
speech_gen.speech_generate("以上が今回おすすめする観光プランになります。何か質問あれば何でも聞いてください！")
reco_after_prompt = f"""
    あなたは旅行代理店の接客のプロです。
    この度のお客様は京都市内の観光を目的としてご来店されました。
    対話の結果お客さんは以下の観光地を経由する旅行になりました。
    {trg2spotTitle}
    出発地は{start_point} で、到着地は、{end_point}です。
    そしてこれらの観光地に以下の道順でいくことも決まっています。
    {journey_ls}
    これらの情報をもとに、今からお客様からの質疑応答があるので適切に回答し、接客を行ってください。
    文章は1文程度で簡潔に答え、相手が応答できない形で終えてください。つまり、話題を終える会話をすることです。
"""

user_input_log_after_recommend = [{"role": "system", "content":reco_after_prompt}]

while True:
    user_input_text = voice_recog.recognize()
    user_input_log_after_recommend.append({"role": "user", "content":user_input_text})
    
    response_queue = queue.Queue()
    speech_thread = threading.Thread(target=yield_speech_message, args=(RobotNLG.yield_GPT4_message, user_input_text, str(reco_after_prompt), user_input_log_after_recommend))
    speech_thread.start()
    stop_generation = False
    async_speech_generate()
    
    user_input_log_after_recommend.append({"role": "assistant", "content":speech_gen})
    
    #終了シグナルの判定
    if check_time_exceeded(start_time,threshold_minutes=20):
        break
    speech_gen.speech_generate("他に質問ありますでしょうか")
#===================================================================================================
# +++++++++++++++++++++++++++++++ 終わりの挨拶 ++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
motion_gen.play_motion("greeting_deep")
speech_gen.speech_generate("申し訳ありません、非常に名残惜しいですが、お時間となってしまいました。以上で案内を終了します。ありがとうございました。")

#===================================================================================================
# +++++++++++++++++++++++++++++++ 会話終了後の処理 ++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================

SectionPrint("NLU結果出力")
# # 会話の終了後、作成されたMongoDBのデータを出力
Dialog_mongodb.print_collection_data(unique_id)