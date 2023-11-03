# mongo_tools.py
import uuid
from datetime import datetime
from pymongo import MongoClient
from tabulate import tabulate
import pandas as pd


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
    
    def insert_initial_data(self):
        # 与えられたコレクション名でコレクションを指定
        
        # 初期データの定義
        initial_data = {
            "LGenre": [],
            "MGenre": [],
            "Genre": [],
            "SightOption": [],
            "Time": [],
            "DayOfTheWeek": [],
            "Traffic": [],
            "Dialog_log":[],
        }

        # 初期データを挿入
        self.collection.insert_one(initial_data)
        
    def update_data(self, json_data):
        
        # 既存のデータを取得
        existing_data = self.collection.find_one()
        
        # 新しいJSONデータを既存のデータと結合
        for key, new_values in json_data.items():
            if key in existing_data:
                # 重複や空白のエントリを削除するためにセットを使用
                merged_values = list(set(existing_data[key] + new_values))
                merged_values = [value for value in merged_values if value]  # 空白のエントリを削除
                existing_data[key] = merged_values
            else:
                existing_data[key] = new_values
        self.collection.replace_one({'_id': existing_data['_id']}, existing_data)
        
    def fetch_data_by_id(self):
        """
        指定したコレクション名に基づいてデータを取得します。
        
        Returns:
        dict: コレクションから取得したデータ
        """
        data = self.collection.find_one()  # コレクションの最初のドキュメントを取得
        if data:
            del data['_id']
            del data['Dialog_log']
        return data
    
    def add_to_dialog_log(self, role_text, content_text):
        # Dialog_log配列に追加するドキュメントを定義
        new_entry = {"role": role_text, "content": content_text}
        
        # $pushオペレータを使用して配列に新しいエントリを追加
        self.collection.update_one({}, {'$push': {'Dialog_log': new_entry}})
        
    def print_collection_data(self):
        # 全てのドキュメントを取得
        data = list(self.collection.find({}))
        
        if not data:
            print("No data found in the collection.")
            return

        # User_text と System_text を除外する
        doc = data[0]  # 最初のドキュメントを取得（他のドキュメントも同じキーを持つと仮定）
        del doc['Dialog_log']
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