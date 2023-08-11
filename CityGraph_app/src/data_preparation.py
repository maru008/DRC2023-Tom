#ここにはRedisGraphに入れるデータの準備を行う
import requests
import json
from tqdm import tqdm
import configparser
import requests
import json
import os
import googlemaps
# =====================================================================================================================
#APIキーなどの定義
# =====================================================================================================================
def read_config():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, '../../config.ini')
    config.read(config_path)
    return config

config_obj = read_config()
RURUBU_API_KEY = "appid=" + str(config_obj.get("API_Key", "RURUBU"))
GOOGLE_API_KEY = str(config_obj.get("API_Key","Google"))

# =====================================================================================================================
#ルルブAPIから観光地データを取り出して，データを保存する
# =====================================================================================================================
# 出力のパス設定
save_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/output_data/RURUBU_results_KyotoCity.json')
# ファイルが存在するかチェック
if os.path.exists(save_path):
    print("RURUBUAPIから取得した観光地ファイルがすでに存在します。スキップします。")
else:
    urlbase = "https://www.j-jti.com/appif/sight?"
    # 京都のGISコードを全て取得
    with open('../data/preparation_data/Kyoto_GIS_Code.json', 'r') as file:
        kyoto_gis_codes = json.load(file)
    # 全ての結果を保存するリスト
    all_results = []

    for district, code in tqdm(kyoto_gis_codes.items(), desc="Processing districts"):
        query = f"&jis={code}&responsetype=json"
        requesturl = urlbase + RURUBU_API_KEY + query
        response = requests.get(requesturl)
        result = json.loads(response.text)
        TotalResult_num = result[0]['TotalResults']
        page_size = len(result[0]['SightList'])
        # 必要なページ数
        num_pages = (TotalResult_num + page_size - 1) // page_size

        for page in range(num_pages):
            query = f"&jis={code}&responsetype=json&page={page + 1}"
            requesturl = urlbase + GOOGLE_API_KEY + query
            response = requests.get(requesturl)
            result = json.loads(response.text)

            if len(result) > 0 and len(result[0]["SightList"]) > 0:
                add_ls = [sight for sight in result[0]['SightList']]
                all_results.extend(add_ls)

    # JSONファイルとして保存
    with open(os.path.join(save_path, 'RURUBU_results_KyotoCity.json'), 'w',encoding='utf-8') as file:
        json.dump(all_results, file, ensure_ascii=False)

    print(f"保存された観光地数：{len(all_results)}")
    
# =====================================================================================================================
#京都市内の駅を取り出して，緯度経度を計算，データを保存する
# =====================================================================================================================
save_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/output_data/stations_geocode.json')

if os.path.exists(save_path):
    print("GoogleAPIから取得した駅Geocodeファイルがすでに存在します。スキップします。")
else:
    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
    # 駅名のファイルを開く
    with open('Stations_KyotoCity.txt', 'r', encoding='utf-8') as file:
        station_names = file.readlines()

    # 結果を保存するための辞書
    result = {}

    for idx, station_name in tqdm(enumerate(station_names),total=len(station_names)):
        query = station_name.strip() + ", Kyoto, Japan"

        # Geocoding APIを呼び出し
        geocode_result = gmaps.geocode(query)
        # 緯度と経度を取得
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']

        # 結果を辞書に保存
        result[idx] = {
            'station_name': station_name,
            'latitude': lat,
            'longitude': lng
        }

    # JSONファイルに保存
    with open('stations_geocode.json', 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)

    print("緯度と経度が stations_geocode.json ファイルに保存されました。")