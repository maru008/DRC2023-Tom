import requests
import json
import datetime

today = datetime.datetime.utcnow().date()  # 現在のUTC日付を取得
tomorrow = today + datetime.timedelta(days=1)  # 明日の日付を計算
fixed_time = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 7, 0)  # 明日の7時に固定

formatted_time = fixed_time.strftime('%Y-%m-%dT%H:%M:%S') 

NAVITIME_move_define = {
  "walk": "徒歩",
  "car": "車",
  "bicycle": "自転車",
  "domestic_flight": "航空路線",
  "ferry": "フェリー",
  "superexpress_train": "新幹線",
  "sleeper_ultraexpress": "寝台特急",
  "ultraexpress_train": "特急",
  "express_train": "急行",
  "rapid_train": "快速",
  "semiexpress_train": "有料列車",
  "local_train": "普通列車",
  "shuttle_bus": "長距離バス"
}

way_ls = [
    "domestic_flight",      #航空路線
    "superexpress_train",   #新幹線
    "sleeper_ultraexpress", #寝台特急
    "ultraexpress_train",   #特急
    "express_train",        #急行
    "rapid_train",          #快速
    "semiexpress_train",    #有料列車
    "local_train",          #普通列車
    "shuttle_bus"           #長距離バス
]

class NAVITME:
    def __init__(self,config,lat_spot1,long_spot1,lat_spot2,Long_spot2):
        self.X_RapidAPI_Key = config.get("API_Key","NAVITIME")
        self.START_LAT = str(config.get("Other_Info","Devise_Lat"))
        self.START_LONG = str(config.get("Other_Info","Devise_Long"))
        
        self.lat_spot1 = str(lat_spot1)
        self.long_spot1 = str(long_spot1)
        self.lat_spot2 = str(lat_spot2)
        self.Long_spot2 = str(Long_spot2)
    
    def request_NAVITIME(self):
        url = "https://navitime-route-totalnavi.p.rapidapi.com/route_transit"
        querystring = {
                    "start":f"{self.START_LAT},{self.START_LONG}",
                    "goal":f"{self.START_LAT},{self.START_LONG}",
                    "start_time":formatted_time,
                    "via":'[{"lat":'+self.lat_spot1+',"lon":'+self.long_spot1+'},{"lat":'+self.lat_spot2+',"lon":'+self.Long_spot2+'}]',
                    "term":"1440",
                    "limit":"1",
                    "datum":"wgs84",
                    "coord_unit":"degree"
                }
        headers = {
            "X-RapidAPI-Key": self.X_RapidAPI_Key,
            "X-RapidAPI-Host": "navitime-route-totalnavi.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        return response.json()

    def get_route_text(self,trg_i,spot_title_ls):
        res_data = self.request_NAVITIME()
        journeys,total_move_time_minutes = format_journey(res_data,trg_i,spot_title_ls)
        return journeys,total_move_time_minutes

def format_journey(data,trg_i,spot_title_ls):
    journeys = []
    journey = ""
    prev_point = "start"  # 初期値として'start'を設定
    move_type = ""
    time = ""
    total_move_time_minutes = 0
    spot_i = 0
    for i in range(len(data["items"][0]["sections"])):
        sec_i = data["items"][trg_i]["sections"][i]
        type_i = sec_i['type']

        if type_i == "move":
            move_type = sec_i["move"]
            time = sec_i['time']
            line_name = sec_i["line_name"]

        elif type_i == "point":
            point_name = sec_i["name"]

            # "経由地" で区切る必要がある場合
            if point_name == "経由地":
                point_name = spot_title_ls[spot_i]
                spot_i += 1
                # 現在の旅程をリストに追加し、新しい旅程を開始
                if journey:  # journeyが空でない場合のみ追加
                    journeys.append(journey.strip())  # 最後の改行を削除
                journey = ""
                

            # 前のポイントから現在のポイントまでの移動を記録し、改行コードを追加
            if point_name != prev_point:
                journey += f"{prev_point} -> ({line_name}) -> {point_name}\n"
                prev_point = point_name  # 現在のポイントを更新
                total_move_time_minutes += time #時間を計測

    # 最後の旅程をリストに追加
    if journey:  # journeyが空でない場合のみ追加
        journeys.append(journey.strip())  # 最後の改行を削除
    
    return journeys, total_move_time_minutes