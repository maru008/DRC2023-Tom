import json

from mongodb_tools_Dialog import MongoDB

mongodb = MongoDB("Sightseeing_Spot_DB")

def read_json_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)
    

def import_data_to_mongodb(data, collection):
    for item in data:
        collection.insert_one(item)

# JSONファイルのパスを指定
filename = "../../../Sightseeing_Spot_data/data/output_data/RURUBU_results_KyotoCity_for_DRC2023.json"

# JSONファイルからデータを読み込む
data = read_json_file(filename)

# MongoDBに接続
mongodb = MongoDB("Sightseeing_Spot_DB")
collection = mongodb.db['sightseeing_spots']  # コレクション名は任意で変更可能

# データをMongoDBにインポート
import_data_to_mongodb(data, collection)