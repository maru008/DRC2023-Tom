import requests
import json
from tqdm import tqdm
import configparser
import requests
import json
import os


def read_config():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, '../../config.ini')
    config.read(config_path)
    return config

urlbase = "https://www.j-jti.com/appif/sight?"
# APIキーの取得
config_obj = read_config()
apikey = "appid=" + str(config_obj.get("API_Key", "RURUBU"))

# 京都のGISコードの取得
with open('../data/Kyoto_GIS_Code.json', 'r') as file:
    kyoto_gis_codes = json.load(file)

# 全ての結果を保存するリスト
all_results = []

for district, code in tqdm(kyoto_gis_codes.items(), desc="Processing districts"):
    query = f"&jis={code}&responsetype=json"
    requesturl = urlbase + apikey + query
    response = requests.get(requesturl)
    result = json.loads(response.text)
    TotalResult_num = result[0]['TotalResults']
    
    if len(result) > 0 and len(result[0]["SightList"]) > 0:
        first_sight = result[0]["SightList"][0]
        for key, value in first_sight.items():
            print(f"{key}: {value}")
    print(TotalResult_num)
    print(len(result[0]['SightList']))
    add_ls = [result[0]['SightList'][i] for i in range(TotalResult_num)]
    all_results.extend(add_ls)

# 保存先ディレクトリのパスを設定
save_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data')

# JSONファイルとして保存
with open(os.path.join(save_path, 'RURUBU_results_KyotoCity.json'), 'w',encoding='utf-8') as file:
    json.dump(all_results, file, ensure_ascii=False)

print(f"保存された観光地数：{len(all_results)}")
