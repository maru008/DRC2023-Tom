# main.py
import os
import sys
import datetime
import time
import json
import threading

from utils.config_reader import read_config
from utils.general_tool import SectionPrint, Create_dialog_log
from utils.TCPserver import SocketConnection
from utils.NAVITIME_Route_serach import NAVITME
from utils.determine_shot import *
from utils.judge_break import judge_roop_break

from ServerModules.speech_generation import SpeechGeneration
from ServerModules.voice_recognition import VoiceRecognition
from ServerModules.face_expression_generation import ExpressionGeneration
from ServerModules.motion_generation import MotionGeneration
from ServerModules.sight_view import SightViewTCPServer

from DialogModules.NLGModule import NLG 
from DialogModules.Add_Hesitation import add_hesitation

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
console_input = input("GPTのAPIを使いますか?(使わない場合おうむ返しになります)(y/n):")
if console_input == "n":
    USE_GPT_API = False
console_input = input("いい淀みを付与しますか？:(y/n)")
if console_input == "y":
    ADD_HESITATION = True
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
sight_view = SightViewTCPServer(DIALOG_MODE,IP,config.get("Server_Info","SiteViewer_port"))
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
# +++++++++++++++++++++++++++++++ 非同期処理用関数 +++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
def async_speech_generate(text):
    speech_gen.speech_generate(text)
    
def async_send_data(data):
    socket_conn.send_data(data)
#===================================================================================================
# +++++++++++++++++++++++++++++++ 対話開始 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
#  ユーザとシステムのログを記録
user_input_text_ls = []
system_output_text_ls = []
resulting_sight_id_mtx = []
#最初の時間を記録
start_time = datetime.datetime.now()
#お辞儀
motion_gen.play_motion("greeting_deep")
speach_t = """こんにちは！旅行代理店ロボットのしょうこです．今回お客様は京都への旅行を考えていると聞きました．私との会話でお客様に最適な観光地を見つけるお手伝いをします！何か旅行で体験したいことなどを教えて下さい．よろしくお願いします．"""
speech_gen.speech_generate(speach_t)
system_output_text_ls.append(speach_t)
user_input_log = [{"role": "system", "content":ChatGPT_prompt_text}]

#進行を記録
Dialog_turn_num = 0
already_serach_json = []
while True:
    # 対話状態更新
    Dialog_turn_num += 1
    current_time = datetime.datetime.now()
    #ブレークジャッジ(Judge_break_boolがtureならループを抜ける)
    Judge_break_bool = judge_roop_break(resulting_sight_id_mtx,Dialog_turn_num,start_time,current_time)
    
    # 発話認識
    motion_gen.play_motion("nod_slight")
    user_input_text = voice_recog.recognize()
    
    motion_gen.play_motion("nod_slight")
    
    user_input_log.append({"role": "user", "content":user_input_text})
    
    if user_input_text in ["終了","quit","q"]:
        break
    
    # GPTを使うかどうか
    if USE_GPT_API:
        response_text = RobotNLG.GPT4(user_input_text,ChatGPT_prompt_text,user_input_log)
    else:
        response_text = user_input_text+"ってなんですか？"
        
    #===================================================================================================
    # 非同期処理開始
    if ADD_HESITATION:#いい淀みを付与
        response_text = add_hesitation(response_text)
    speech_thread = threading.Thread(target=async_speech_generate, args=(response_text,))#発話指示
    send_data_thread = threading.Thread(target=async_send_data, args=(str([unique_id, user_input_text]),))#NLUサーバに文字列を送る（DBへの追加は向こう側）
    
    speech_thread.start()
    send_data_thread.start()
    
    # 必要に応じて、後の処理で両方のスレッドが終了するのを待つ
    speech_thread.join()
    send_data_thread.join()    
    
    ## ユーザとロボットのテキスト追加
    user_input_text_ls.append(user_input_text)
    system_output_text_ls.append(response_text)
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
    
    for combination in all_combinations:
        if str(combination) not in already_serach_json:
            condition_json = json.dumps(combination)
            sight_ids = Sightseeing_mongodb.get_sight_ids_by_multiple_conditions(condition_json)
            if len(sight_ids) > 2 and len(sight_ids) < 100:
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
        # response_text = change_subject(data_as_json)
        # speech_gen.speech_generate(response_text)
        user_input_log = [{"role": "system", "content":ChatGPT_prompt_text}]
        user_input_log.append({"role": "assistant", "content":response_text})

#===================================================================================================
# +++++++++++++++++++++++++++++++ 4つの観光地を説明する ++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================

#画面表示するものを送る
Select4_Bool = False
print("select 4 spot...")
sightID_ls = select4spot(resulting_sight_id_mtx)
if sightID_ls is None:
    sightID_ls = [80026003,80026022,80025993,80025990] #得られなかったら仮の4つ選ぶ
    result_user_json ={}
else:
    result_user_json = data_as_json
    Select4_Bool = True
sightTitle_ls = [Sightseeing_mongodb.get_title_by_sight_id(sightID_i) for sightID_i in sightID_ls]
print("選ばれた観光地リスト: ",sightTitle_ls)
#この4つを選んだ基準を話す===================================================================================
# 非同期処理関数定義========================================================================================
def async_speach_json_result():
    speach_t ="ありがとうございます．今回の旅行がどういうものか，そしてあなたがどんな人かわかりました！それではいくつか観光地を検索いたします．少しお待ちください．"
    speech_gen.speech_generate(speach_t)
    system_output_text_ls.append(speach_t)
    
def async_generate_spot_reason(sightTitle_ls,user_json):
    global spot_reason_text
    SpotReason_prompt_path = os.path.join(script_dir,"DialogModules/Prompts/Spot_reason.txt")
    with open(SpotReason_prompt_path, 'r', encoding='utf-8') as f:
        SpotReason_prompt_text = f.read()
    input_text = str(sightTitle_ls) + "\n" + json.dumps(user_json)
    spot_reason_text = RobotNLG.GPT4(input_text,SpotReason_prompt_text,[])
#4つ選ばれていたら非同期処理開始
if Select4_Bool:
    thread1 = threading.Thread(target=async_speach_json_result, args=())
    thread2 = threading.Thread(target=async_generate_spot_reason, args=(sightTitle_ls,result_user_json,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    #理由の発話
    speech_gen.speech_generate(spot_reason_text)
    system_output_text_ls.append(spot_reason_text)
else:
    speach_t = "申し訳ありません．お客様に合致した観光地を見つけることができませんでした．今回は京都で代表的な観光地を上げさせていただきます．"
    speech_gen.speech_generate(speach_t)
    system_output_text_ls.append(speach_t)
    
speach_t = "それでは，4つそれぞれについて説明させていただきます．"
speech_gen.speech_generate(speach_t)
system_output_text_ls.append(speach_t)
#画像表示サーバにデータを送る============================================================================
view_spot_json = Sightseeing_mongodb.create_send_json(sightID_ls)
sight_view.send_data(view_spot_json)
#  観光地紹介用GPT============================================================================
SpotIntro_prompt_path = os.path.join(script_dir,"DialogModules/Prompts/Spot_intro.txt")
with open(SpotIntro_prompt_path, 'r', encoding='utf-8') as f:
    SpotIntroGPT_prompt_text = f.read()
# 非同期処理用の関数============================================================================
def async_speach_view_monitor(head_text, title, results, index):
    speach_text = head_text  + title + "の写真と地図です．ご覧ください．"
    speech_gen.speech_generate(speach_text)
    system_output_text_ls.append(speach_text)
    results[index] = speach_text

def async_intro_spot(spotdesc_text):
    global response_from_intro_spot
    # response_text = RobotNLG.GPT4(spotdesc_text,SpotIntroGPT_prompt_text,[])
    response_text = "省略"
    response_from_intro_spot = response_text
    return response_text

# 観光地の紹介を開始============================================================================
head_text_ls = ["まず左上は，","次に右上は，","その左下は，","最後に右下は，"]
# 結果を保存するためのリストを用意
spoken_texts = [None] * len(sightID_ls)
for i,sightID_i in enumerate(sightID_ls):
    title_i = sightTitle_ls[i]
    #DBから説明文取得
    desc_i = Sightseeing_mongodb.get_summary_by_sight_id(sightID_i)
    
    thread1 = threading.Thread(target=async_speach_view_monitor, args=(head_text_ls[i], title_i, spoken_texts, i))
    thread2 = threading.Thread(target=async_intro_spot, args=(desc_i,))

    # スレッドを開始
    thread1.start()
    thread2.start()

    # ここで、両方のスレッドが終了するのを待ちます
    thread1.join()
    thread2.join()
    speech_gen.speech_generate(response_from_intro_spot)
    time.sleep(1)
now_screen_state = '\n'.join(spoken_texts)

#===================================================================================================
# +++++++++++++++++++++++++++++++ ２つの観光地を絞る ++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
speech_gen.speech_generate("これら４つの観光地から二つの観光地を選んでください，よろしくお願いします．")

#二つの観光地を選ぶ段階---------------------------------------------------------------------------------
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
    user_input_text_ls.append(user_input_text)
    response_text = RobotNLG.GPT4(user_input_text,choice_two_spot_prompt,[])
    trg2spotid = eval(response_text)
    print("得られたIDのリスト：",trg2spotid)
    if len(trg2spotid) == 2:
        break
    elif len(trg2spotid) <= 1:
        speach_text = "すみません,2つを選んでください．もう一度お願いします．"
        
    elif len(trg2spotid) > 2:
        speach_text = "すみません,2つに絞ってください．もう一度お願いします．"
        
    else:
        speach_text = "すみません,理解できませんでした．もう一度お願いします．"
    speech_gen.speech_generate(speach_text)
    system_output_text_ls.append(speach_text)

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

def async_speach_spot(trg2spotid,trg2spotTitle):
    speach_t = f"ありがとうございます．お客様が行きたいスポットは{trg2spotTitle[0]}と{trg2spotTitle[1]}ですね．"
    speech_gen.speech_generate(speach_t)
    system_output_text_ls.append(speach_t)
    sight_view.send_data(Sightseeing_mongodb.create_send_json(trg2spotid))
    speach_t = "それではこの店から出発し，公共交通機関で観光地を巡り，帰ってくるプランを検索いたします．少しお待ちください．"
    speech_gen.speech_generate(speach_t)
    system_output_text_ls.append(speach_t)

def async_search_route(trg2spotid):
    global route_desc_text

    journey_ls = NAVITME_serach.get_route_text(0)#この0は候補の番目

    route_info_json = {
        "start_end_spot":["JTBユニモール名古屋","JTBユニモール名古屋"],
        "via_spot":trg2spotTitle,
        "route_desc":journey_ls,
    }
    response_text = RobotNLG.GPT4(str(route_info_json),routeInfo_prompt_text,[])
    route_desc_text = response_text

#並列処理--------------------------------------------------------------------------------------------
print("-------------start multi-thread processing (speach and serach route)-------------")
thread1 = threading.Thread(target=async_speach_spot, args=(trg2spotid,trg2spotTitle))
thread2 = threading.Thread(target=async_search_route, args=(trg2spotid,))
# スレッドを開始
thread1.start()
thread2.start()
# ここで、両方のスレッドが終了するのを待ちます
thread1.join()
thread2.join()
speech_gen.speech_generate(route_desc_text)
system_output_text_ls.append(route_desc_text)


## 対話ログを追加--------------------------------------------------------------------------------------------
user_text_json = {
    "User_text":user_input_text_ls
}
system_text_json = {
    "System_text":system_output_text_ls
}
Dialog_mongodb.update_data(unique_id,user_text_json)
Dialog_mongodb.update_data(unique_id,system_text_json)
#===================================================================================================
# +++++++++++++++++++++++++++++++ LangChainとの対話 ++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
speech_gen.speech_generate("以上が今回おすすめする観光プランになります．何か質問あれば何でも聞いてください！")


from langchain.document_loaders import MongodbLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.memory import ConversationSummaryMemory
from langchain.schema.document import Document

OPEN_API_KEY = config.get("API_Key","OpenAI")

loader = MongodbLoader(
    connection_string='mongodb://localhost:27017/',
    db_name='DRC2023_Dialog_DB',
    collection_name=unique_id
)

# Document インスタンスを作成
documents = loader.load()
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=0)
# all_splits = text_splitter.split_documents(documents)
# print(all_splits)
embeddings = OpenAIEmbeddings(openai_api_key=OPEN_API_KEY)
vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings)

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

# Langchain_prompt_path = os.path.join(script_dir,"DialogModules/Prompts/LangChain_prompt.txt")
# with open(Langchain_prompt_path, 'r', encoding='utf-8') as f:
#     # ファイルの内容を読み込む
#     Langchain_prompt_text = f.read()


llm = ChatOpenAI(openai_api_key=OPEN_API_KEY,model="gpt-4")
retriever = vectorstore.as_retriever()
memory = ConversationSummaryMemory(llm=llm,memory_key="chat_history",return_messages=True)
qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)

i = 0
while True:
    user_input_text = voice_recog.recognize()
    
    systyem_output_text = qa(user_input_text)["answer"]
    speech_gen.speech_generate(systyem_output_text)
    
    if i >= 3:
        break
    i += 1
#===================================================================================================
# +++++++++++++++++++++++++++++++ 終わりの挨拶 ++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
motion_gen.play_motion("greeting_deep")
speech_gen.speech_generate("以上で案内を終了します．ありがとうございました．")



#===================================================================================================
# +++++++++++++++++++++++++++++++ 会話終了後の処理 ++++++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================


SectionPrint("NLU結果出力")
# # 会話の終了後、作成されたMongoDBのデータを出力
Dialog_mongodb.print_collection_data(unique_id)