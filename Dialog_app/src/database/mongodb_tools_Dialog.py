# mongo_tools.py
import uuid
from datetime import datetime
from pymongo import MongoClient
from tabulate import tabulate
import pandas as pd
import json

import socket

class MongoDB:
    """
    MongoDBデータベースとの接続を管理するクラス。

    このクラスを使用すると、指定したMongoDBデータベースに接続し、
    データを追加、取得、またはデータベースをリセットすることができます。

    使用例：
    db = MongoDB('my_database')
    db.add_to_array('my_collection', 'my_field', 'my_data')
    db.print_all_tables(['_id', 'my_field'])
    """
    def __init__(self,db_name):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[db_name]
        
    def reset_database(self):
        """
        このデータベースの全てのコレクションを削除し、データベースをリセットします。

        警告：このメソッドは全てのデータを削除します。
        データのバックアップが必要な場合は、このメソッドを実行する前にデータをバックアップしてください。
        """
        for collection_name in self.db.list_collection_names():
            self.db.drop_collection(collection_name)
    

    def get_unique_collection_name(self):
        """
        データベース内で一意のコレクション名を生成します。

        UUIDを使用して一意の識別子を生成し、それがデータベース内の既存のコレクション名と衝突しないことを確認します。
        
        Returns:
        str: 生成された一意のコレクション名。
        """
        unique_name = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        if unique_name not in self.db.list_collection_names():
            self.collection = self.db[unique_name]
            return unique_name
    
    def insert_initial_data(self, collection_name):
        # 与えられたコレクション名でコレクションを指定
        collection = self.db[collection_name]
        
        # 初期データの定義
        initial_data = {
            "LGenre": [],
            "MGenre": [],
            "Genre": [],
            "SightOption": [],
            "Time": [],
            "DayOfTheWeek": [],
            "Traffic": [],
            "User_text":[],
            "System_text":[],
        }

        # 初期データを挿入
        collection.insert_one(initial_data)
        
    def update_data(self, collection_name, json_data):
        collection = self.db[collection_name]
        
        # 既存のデータを取得
        existing_data = collection.find_one()
        
        # 新しいJSONデータを既存のデータと結合
        for key in json_data:
            # もし新しいデータが空でないなら、それを追加
            if json_data[key] and isinstance(json_data[key], list) and json_data[key][0]:
                new_value = json_data[key][0].strip()  # 前後の空白を取り除く
                if not new_value:  # 新しいデータが空白の場合、スキップ
                    continue

                # 既存のデータが空の場合
                if not existing_data.get(key):
                    existing_data[key] = [new_value]  # リストとして新しいデータをセット
                # 既存のデータが空でない場合、かつ新しいデータが既存のリストに存在しない場合
                elif new_value not in existing_data[key]:
                    if isinstance(existing_data[key], list):
                        existing_data[key].append(new_value)
                    else:
                        existing_data[key] = [existing_data[key], new_value]

        # ここで、空白のリスト [''] を削除する
        for key, value in existing_data.items():
            if value == ['']:
                del existing_data[key]

        # データを更新
        collection.update_one({}, {'$set': existing_data})
    
    def fetch_data_by_id(self, collection_name):
        """
        指定したコレクション名に基づいてデータを取得します。
        
        Args:
        collection_name (str): データを取得するコレクションの名前
        
        Returns:
        dict: コレクションから取得したデータ
        """
        collection = self.db[collection_name]
        data = collection.find_one()  # コレクションの最初のドキュメントを取得
        if data:
            del data['_id']
            del data['User_text']
            del data['System_text']
        return data
    
    def print_collection_data(self, collection_name):
        collection = self.db[collection_name]

        # 全てのドキュメントを取得
        data = list(collection.find({}))
        
        if not data:
            print("No data found in the collection.")
            return

        # User_text と System_text を除外する
        doc = data[0]  # 最初のドキュメントを取得（他のドキュメントも同じキーを持つと仮定）
        del doc['User_text']
        del doc['System_text']
        del doc['_id']

        # データを縦に整形
        # リスト内の全ての要素を表示
        table_data = [[key, ', '.join(value) if value else "EMPTY"] for key, value in doc.items()]

        # tabulate を使用してデータを表形式で出力
        headers = ["key", "value"]
        print(tabulate(table_data, headers=headers, tablefmt='grid'))


def check_db_exists(db_name):
    client = MongoClient('mongodb://localhost:27017/')
    # 現在のデータベース一覧を取得
    db_list = client.list_database_names()
    # 指定したデータベース名が一覧に存在するか確認
    return db_name in db_list


#===================================================================================================
# +++++++++++++++++++++++++++++++ 観光地DB関連メソッド ++++++++++++++++++++++++++++++++++++++++++++++++
#===================================================================================================
class SightseeingDBHandler:
    def __init__(self,db_name):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[db_name]

    def build_query(self, base_criteria, genre_value, genre_type="LGenre"):
        criteria = base_criteria.copy()
        criteria[genre_type] = [genre_value]
    
        query = {}
    
        if "LGenre" in criteria and criteria["LGenre"]:
            query["GenreList.LGenre.Name"] = {"$in": criteria["LGenre"]}
            
        if "MGenre" in criteria and criteria["MGenre"]:
            query["GenreList.MGenre.Name"] = {"$in": criteria["MGenre"]}
            
        if "Genre" in criteria and criteria["Genre"]:
            query["GenreList.Genre.Name"] = {"$in": criteria["Genre"]}
            
        if "SightOption" in criteria and criteria["SightOption"]:
            query["SightOptionList.SightOptionName"] = {"$in": criteria["SightOption"]}
        
        # if "Time" in criteria and criteria["Time"]:
        #     query["Time"] = {"$in": criteria["Time"]}
            
        # if "Traffic" in criteria and criteria["Traffic"]:
        #     query["$or"] = [
        #         {"Traffic1": {"$in": criteria["Traffic"]}},
        #         {"Traffic2": {"$in": criteria["Traffic"]}}
        #     ]
        return query
    
    def fetch_sight_ids(self, criteria, genre_type="LGenre"):
        collection = self.db['sightseeing_spots']
        
        sight_ids = {}
        
        for genre_value in criteria[genre_type]:
            if not genre_value:  # Skip empty values
                continue
            query = self.build_query(criteria, genre_value, genre_type)
            distinct_sight_ids = collection.distinct("SightID", query)
            sight_ids[genre_value] = distinct_sight_ids
            
        return sight_ids

    def id2info_forView(self,SightID):
        collection = self.db["sightseeing_spots"]
        data = collection.find_one({'SightID': SightID})
        # データから各情報を取得
        if data:
            title = data['Title']
            image_files = [photo['URL'] for photo in data['PhotoList']]
            latitude = data['LatitudeW10']
            longitude = data['LongitudeW10']
        else:
            print(f"No data found for SightID: {SightID}")
        
        return title, image_files, latitude, longitude
    
    def create_send_json(self,ID_ls):
        res_json = {}
        res_json['Num'] = len(ID_ls)
        for i, ID_i in enumerate(ID_ls):
            title,image_files,latitude, longitude = self.id2info_forView(ID_i)
            res_json[f"ImageURL{i+1}"] = f'https://www.j-jti.com/Storage/Image/Product/SightImage/Org/{image_files[0]}'
            res_json[f"MapURL{i+1}"] = f'https://www.google.co.jp/maps/@{latitude},{longitude}15z'
            res_json[f"Name{i+1}"] = title
        return res_json
        
class SightViewTCPServer():
    def __init__(self, ip,port):
        self.ip = ip
        self.port = int(port)
        
    def send_data(self,dictsite):
        sock = socket.socket(socket.AF_INET)
        sock.connect((self.ip, self.port))
        
        json_data = json.dumps(dictsite).encode('utf-8')
        sock.send(json_data)
        print("send data")

        rcv_data = sock.recv(128)            
        rcv_data = rcv_data.decode('utf-8')
        rcvdict = json.loads(rcv_data)
        print("result: " + rcvdict['Return'])