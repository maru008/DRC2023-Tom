from pymongo import MongoClient
import json
from tabulate import tabulate

class MongoDB:
    """
    MongoDBデータベースとの接続を管理するクラス。(forNLU)

    このクラスを使用すると、指定したMongoDBデータベースに接続し、
    データを追加、取得、またはデータベースをリセットすることができます。

    使用例：
    db = MongoDB('my_database')
    db.add_to_array('my_collection', 'my_field', 'my_data')
    db.print_all_tables(['_id', 'my_field'])
    """
    def __init__(self,db_name):
        self.client = MongoClient('mongodb://db:27017/')
        self.db = self.client[db_name]
    
    def switch_collection(self, collection_name):
        self.collection = self.db[collection_name]

    
    def update_data(self, collection_name, json_data):
        collection = self.db[collection_name]
        
        # 既存のデータを取得
        existing_data = collection.find_one()
        
        # 新しいJSONデータを既存のデータと結合
        for key in json_data:
            # もし新しいデータが空でないなら、それを追加
            if json_data[key] and isinstance(json_data[key], list):
                # 既存のデータが空の場合
                if not existing_data.get(key):
                    # print(f"[DEBUG] Key '{key}' not found in existing data. Creating new key.")
                    existing_data[key] = json_data[key]
                # 既存のデータが空でない場合、かつ新しいデータが既存のリストに存在しない場合
                elif json_data[key][0] not in existing_data[key]:
                    if isinstance(existing_data[key], list):
                        existing_data[key].append(json_data[key][0])
                        # print(f"[DEBUG] Adding {json_data[key][0]} to existing key {key}.")
                    else:
                        existing_data[key] = [existing_data[key], json_data[key][0]]
                        # print(f"[DEBUG] Converted {key} to a list and added {json_data[key][0]}.")

        # データを更新
        result = collection.update_one({}, {'$set': existing_data})

        # if result.modified_count > 0:
        #     print("[DEBUG] Successfully updated the document.")
        # else:
        #     print("[DEBUG] Document was not modified.")

        # デバッグのため、更新後のデータを表示
        data_after_update = collection.find_one()
        # print("[DEBUG] Data after update:", data_after_update)

        
        
    def print_collection_data(self, collection_name):
        collection = self.db[collection_name]

        # 全てのドキュメントを取得
        data = list(collection.find({}))
        
        if not data:
            print("No data found in the collection.", flush=True)
            return

        # User_text と System_text を除外する
        doc = data[0]  # 最初のドキュメントを取得（他のドキュメントも同じキーを持つと仮定）
        del doc['User_text']
        del doc['System_text']
        del doc['_id']

        # データを縦に整形
        table_data = [[key, value[0] if value else ""] for key, value in doc.items()]

        # tabulate を使用してデータを表形式で出力
        headers = ["key", "value"]
        print(tabulate(table_data, headers=headers, tablefmt='grid'), flush=True)
        
    def close_connection(self):
        self.client.close()
        
        