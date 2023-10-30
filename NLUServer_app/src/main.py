import os
import json
import re
from utils.TCP_Server_data import Server
from utils.config_reader import read_config
from utils.mongodb_tool_NLU import MongoDB

from NLUModule.Text_NLU_module import NLU

print("start NLU Server !", flush=True)

server = Server()
server.start_server()

conf_object = read_config()
text_nlu = NLU(conf_object)

script_dir = os.path.dirname(os.path.realpath(__file__))
prompt_path = os.path.join(script_dir,"NLUModule/Prompts/GPT4_NLU.txt")
with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_text = f.read()

# input_text_ls = []
while True:
    received_data, connection = server.accept_connections()
    if received_data is not None:
        mongo_db = MongoDB('DRC2023_Dialog_DB')
        # ここで受け取ったデータを使用できます
        received_data_ls = eval(received_data)
        unique_id = str(received_data_ls[0])
        received_text = received_data_ls[1]
        print("ID:",unique_id, flush=True)
        print("recieve text:",received_text, flush=True)
        if received_text == "終了":
            #MongoDBとの接続を解除
            mongo_db.close_connection()
            # input_text_ls = []
            #フロントとの接続を解除
            connection.close()
        else:
            res = text_nlu.NLU_GPT4(received_text,prompt_text,[])
            # input_text_ls.append({"role": "user", "content":received_text})
            print(res, flush=True)

            try:
                # 正規表現を使用して中括弧で囲まれた部分を抽出
                res = re.sub(r'[^{]*({[^}]*})[^{]*', r'\1', res)
                # JSONのデコードを試みる
                decoded_json = json.loads(res)
                # デコードに成功した場合のみupdate_dataを実行
                mongo_db.update_data(unique_id, decoded_json)
            except json.decoder.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                pass