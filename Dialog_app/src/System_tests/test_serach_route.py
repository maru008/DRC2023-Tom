import os
import json

from utils.Google_Route_Search import search_route
from utils.config_reader import read_config
from DialogModules.NLGModule import NLG 


lat1, long1 = 35.062358211, 135.736914797
lat2, long2 = 35.060411266, 135.75270778

config = read_config()

api_key = config.get("API_Key","Google")
mode = "driving"

res_data = search_route(lat1, long1, lat2, long2, api_key, mode)


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

# 新しいJSON文字列を出力（またはファイルに保存）

print(new_json_string)

RobotNLG = NLG(config)

script_dir = os.path.dirname(os.path.realpath(__file__))
Dialog_prompt_path = os.path.join(script_dir,"DialogModules/Prompts/For_route_search.txt")
with open(Dialog_prompt_path, 'r', encoding='utf-8') as f:
    # ファイルの内容を読み込む
    routeInfo_prompt_text = f.read()
 

print(RobotNLG.ChatGPT(str(new_json_string),routeInfo_prompt_text,[]))
