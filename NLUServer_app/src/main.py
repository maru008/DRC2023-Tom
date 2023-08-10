import os

from utils.receive_data import Server
from utils.config_reader import read_config
from utils.mongodb_tool import MongoDB

from NLUModule.Text_NLU_module import NLU
print("start NLU Server !", flush=True)
server = Server()
server.start_server()

mongo_db = MongoDB('Dialog_system')

conf_object = read_config()
text_nlu = NLU(conf_object)

script_dir = os.path.dirname(os.path.realpath(__file__))
prompt_path = os.path.join(script_dir,"NLUModule/Prompts/GPT4_NLU.txt")
with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_text = f.read()

input_text_ls = []
while True:
    received_data = server.accept_connections()
    if received_data is not None:
        # ここで受け取ったデータを使用できます
        received_data_ls = eval(received_data)
        ID = received_data_ls[0]
        received_text = received_data_ls[1]
        # print("ID:",ID, flush=True)
        print("recieve text:",received_text, flush=True)
        if received_text == "終了":
            mongo_db.close_connection()
            input_text_ls = []
        else:
            res = text_nlu.NLU_GPT4(received_text,prompt_text,input_text_ls)
            input_text_ls.append({"role": "user", "content":received_text})
            print(res, flush=True)
            print("="*100)
            mongo_db.update_document(str(ID), res)
        