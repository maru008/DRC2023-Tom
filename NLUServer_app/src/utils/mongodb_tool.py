from pymongo import MongoClient
import json

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
        self.client = MongoClient('mongodb://db:27017/')
        self.db = self.client[db_name]
    
    def switch_collection(self, collection_name):
        self.collection = self.db[collection_name]

    def update_document(self, user_id, data):
        collection = self.db[user_id]
        if isinstance(data, str):
            data = json.loads(data)

        # ユーザーIDを基にしてドキュメントを検索し、データを更新する
        collection.update_one({'user_id': user_id}, {'$set': data}, upsert=True)

        
    def close_connection(self):
        self.client.close()