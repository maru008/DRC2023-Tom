#ここにはサーバへデータを入れる処理を書く
import os
import json
from tqdm import tqdm
import redis
from redisgraph import Graph, Node, Edge
from geopy.distance import geodesic
import json

input_data_root_path = "../data/"
# =====================================================================================================================
# データの読み込み，準備
# =====================================================================================================================
with open(os.path.join(input_data_root_path,'output_data/KyotoCity_Stations_Info.json'), 'r') as f:
    KyotoCity_Stations_Info = json.load(f)
with open(os.path.join(input_data_root_path,"output_data/RURUBU_results_KyotoCity.json"), 'r') as f:
    RURUBU_SightSpot_data = json.load(f)
with open(os.path.join(input_data_root_path,'preparation_data/KyotoCity_TrainMap.json'), 'r') as f:
    train_lines = json.load(f)
station_coordinates = {station['Station_Name']: (station['latitude'], station['longitude']) for station in KyotoCity_Stations_Info}
# =====================================================================================================================
# 京都市の観光地GDBの作成
# =====================================================================================================================

# KyotoCityGraphという名前でグラフを作成
graph_name = 'KyotoCityGraph'
redis_con = redis.Redis(host='localhost', port=6379)

# すでにグラフが存在する場合、削除
if redis_con.exists(graph_name):
    redis_con.delete(graph_name)

graph = Graph(graph_name, redis_con)

# ノード（駅）を追加
nodes_ref = {}
for station_i in tqdm(KyotoCity_Stations_Info,desc="Input Station node to Redis"):
    add_properties={
        'StationCode': station_i["Station_Name"],
        'StationName': station_i["Station_Name"], 
        'Latitude': station_i["latitude"],
        'Longitude': station_i["longitude"],
        'Trainline': station_i["lines"]
    }
    statiton_node = Node(label='Station', properties=add_properties)
    graph.add_node(statiton_node)
    nodes_ref[station_i["Station_Name"]] = statiton_node

sight_nodes_ref = {}
# ノード（観光地）を追加
for spot_i in tqdm(RURUBU_SightSpot_data,desc="input SightseeingSpot node to Redis"):
    #ここに追加すべきノードのプロパティを入れる(現状はIDと観光地名だけ)
    add_properties={
        "name":spot_i["Title"],'SightID':spot_i["SightID"],
        'latitude': spot_i["LatitudeW10"], 'longitude': spot_i["LongitudeW10"]
    }
    sight_node = Node(label="SightseeingSpot",properties=add_properties)
    graph.add_node(sight_node)
    sight_nodes_ref[spot_i["SightID"]] = sight_node

#-----------------------------------------------------------------------------------
# エッジ（駅間の接続）を追加
for line, station_list in train_lines.items():
    for i in range(len(station_list) - 1):
        station1_name = station_list[i]
        station2_name = station_list[i + 1]
        lat1, lon1 = station_coordinates[station1_name]
        lat2, lon2 = station_coordinates[station2_name]
        distance = geodesic((lat1, lon1), (lat2, lon2)).kilometers
        
        node1 = nodes_ref[station1_name]
        node2 = nodes_ref[station2_name]
        properties={'line': line, 'distance': distance}

        edge = Edge(node1, 'TRAINLINE', node2, properties=properties)
        graph.add_edge(edge)
        
        # 駅2から駅1へのエッジも追加（無向グラフを表現）
        edge_reverse = Edge(node2, 'TRAINLINE', node1, properties=properties)
        graph.add_edge(edge_reverse)


# エッジ（駅と観光地）を追加

for spot_i in tqdm(RURUBU_SightSpot_data,desc="input SightseeingSpot-station edge to Redis"):
    if 'Station' not in spot_i or 'Name' not in spot_i['Station']:
        continue
    #ここに追加すべきノードのプロパティを入れる(現状は最寄り駅だけを取り出す)
    nearest_station = spot_i['Station']["Name"]
    if not nearest_station.endswith("駅"):
        nearest_station += "駅"
    sight_node = sight_nodes_ref[spot_i["SightID"]]
    # 対応する駅ノードを取得
    station_node = nodes_ref.get(nearest_station, None)
    if station_node is not None:
        # エッジを作成して追加
        properties = {'type': 'NEAREST'}  # 必要に応じてプロパティを追加
        edge = Edge(sight_node, 'NEAR', station_node, properties=properties)
        graph.add_edge(edge)
        
        edge_reverse = Edge(station_node, 'NEAR', sight_node, properties=properties)
        graph.add_edge(edge_reverse)
graph.commit()