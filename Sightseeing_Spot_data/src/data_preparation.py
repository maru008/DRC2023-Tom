#ここにはRedisGraphに入れるデータの準備を行う
import requests
import json
from tqdm import tqdm
import configparser
import requests
import json
import os
import re
import googlemaps

from NLUModule.NLU_text import NLU
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

output_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/output_data/')
# =====================================================================================================================
#るるぶAPIから観光地データを取り出して，データを保存する
# =====================================================================================================================
# 出力のパス設定
RURUBU_save_path = os.path.join(output_data_path, 'RURUBU_results_KyotoCity.json')
# ファイルが存在するかチェック
if os.path.exists(RURUBU_save_path):
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
    with open(RURUBU_save_path, 'w',encoding='utf-8') as file:
        json.dump(all_results, file, ensure_ascii=False, indent=4)
    print(f"保存された観光地数：{len(all_results)}")
    
# =====================================================================================================================
#るるぶAPIから取り出された観光地データから駅名を取り出して，緯度経度を計算，データを保存する
# =====================================================================================================================
Station_JSON_save_path = os.path.join(output_data_path, 'KyotoCity_Stations_Info.json')
if os.path.exists(Station_JSON_save_path):
    print("RURUBUAPIとGoogleAPIから取得した最寄り駅一覧テキストファイルがすでに存在します。スキップします。")
else:
    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
    with open(RURUBU_save_path, 'r') as file:
        RURUBU_res_data = json.load(file)
    station_dict_ls = []
    done_stationCode_ls = []
    for spot_i in tqdm(RURUBU_res_data,total=len(RURUBU_res_data),desc="get Station Name and Geocode"):
        if 'Station' not in spot_i or 'Name' not in spot_i['Station']:
            continue
        station_dict = {}
        station_code = spot_i['Station']["Code"]
        if station_code not in done_stationCode_ls:
            done_stationCode_ls.append(station_code)
            station_name = spot_i['Station']["Name"]
            station_name = re.sub(r'\(.*?\)', '', station_name)
            if not station_name.endswith("駅"):
                station_name += "駅"
            station_dict["Station_Code"] = station_code
            station_dict["Station_Name"] = station_name
            query = station_name + ", Kyoto, Japan"
            
            # Geocoding APIを呼び出し
            geocode_result = gmaps.geocode(query)
            
            lat = geocode_result[0]['geometry']['location']['lat']
            lng = geocode_result[0]['geometry']['location']['lng']
            
            station_dict["latitude"] = lat
            station_dict['longitude'] = lng
            station_dict_ls.append(station_dict)
            
    #沿線データにあるものを追加していく．
    station_info_by_lat_long = {(str(s["latitude"]), str(s["longitude"])): s for s in station_dict_ls}
    
    with open('../data/preparation_data/KyotoCity_TrainMap.json', 'r', encoding='utf-8') as file:
        train_map = json.load(file)

    # KyotoCity_TrainMap.jsonの各駅について緯度経度を計算
    for line_name, stations in tqdm(train_map.items(),total=len(train_map.items()),desc="get Station Name and Geocode from trainMap"):
        for station_name in stations:
            query = station_name + ", Kyoto, Japan"
            # Geocoding APIを呼び出し
            geocode_result = gmaps.geocode(query)
            
            latitude = geocode_result[0]['geometry']['location']['lat']
            longitude = geocode_result[0]['geometry']['location']['lng']
            key = (str(latitude), str(longitude))
            
            # 緯度経度が既にKyotoCity_Stations_Info.jsonに存在する場合
            if key in station_info_by_lat_long:
                station = station_info_by_lat_long[(str(latitude), str(longitude))]
                if "lines" not in station:
                    station["lines"] = []
                if line_name not in station["lines"]:
                    station["lines"].append(line_name)
            else:
                # 緯度経度がKyotoCity_Stations_Info.jsonに存在しない場合
                new_station = {
                    "Station_Code": None, # 適切な駅コードを割り当てる
                    "Station_Name": station_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "lines": [line_name]
                }
                station_dict_ls.append(new_station)
                station_info_by_lat_long[key] = new_station
    # 辞書データをJSONファイルとして保存    
    for station in station_dict_ls:
        if "lines" not in station:
            station["lines"] = []
    with open(Station_JSON_save_path, 'w', encoding='utf-8') as file:
        json.dump(station_dict_ls, file, ensure_ascii=False, indent=4)

# =====================================================================================================================
#るるぶAPIから取り出された観光地データから交通情報をNLUする（※処理時間多）
# =====================================================================================================================
RURUBU_TraficInfo_save_path = os.path.join(output_data_path, 'RURUBU_KyotoCity_TraficInfo.json')

# もしファイルが存在するならデータをロード
if os.path.exists(RURUBU_TraficInfo_save_path):
    with open(RURUBU_TraficInfo_save_path, 'r', encoding='utf-8') as file:
        existing_data = json.load(file)
else:
    existing_data = []

with open(RURUBU_save_path, 'r', encoding='utf-8') as f:
    RURUBU_res = json.load(f)

if len(RURUBU_res) == len(existing_data):
    print("RURUBUデータからNLUしたファイルがすでに完成してます。スキップします。")
else:
    # NLUモジュールの準備
    NLU_module = NLU(config_obj)
    prompt_path = os.path.join("./NLUModule/Prompts/Get_Trafic_info.txt")
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_text = f.read()
    
    existing_sight_ids = [entry["SightID"] for entry in existing_data]
    
    # ここから観光地ごとの処理
    for spot_i in tqdm(RURUBU_res,desc="NLU TraficInfo"):
        SightID = spot_i["SightID"]
        if SightID in existing_sight_ids:
            continue
        try:
            Traffic2 = spot_i["Traffic2"] if "Traffic2" in spot_i else ""
            TraficInfoText = spot_i["Traffic1"] +"/" +Traffic2+"/最寄り駅:" + spot_i['Station']["Name"]
            res_json = json.loads(NLU_module.NLU_GPT4(TraficInfoText, prompt_text, []))
            res_json["SightID"] = SightID
            existing_data.append(res_json)
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            with open(RURUBU_TraficInfo_save_path, 'w', encoding='utf-8') as file:
                json.dump(existing_data, file, ensure_ascii=False, indent=4)
            raise

    with open(RURUBU_TraficInfo_save_path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

    print("RURUBUAPIの交通情報を構造化したデータがRURUBU_KyotoCity_TraficInfo.jsonファイルに保存されました。")

