# mongo_tools.py
import uuid
from datetime import datetime
from pymongo import MongoClient
from tabulate import tabulate
import pandas as pd
import pprint

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
    
    
    def add_to_array(self, collection_name, field_name, data):
        """
        MongoDBの指定したコレクションにデータを追加するメソッド。

        Parameters:
        collection_name (str): データを追加するコレクションの名前。
        field_name (str): データを追加するフィールドの名前。
        data: 追加するデータ。任意の型が可能。

        Returns:
        int: 追加に成功したドキュメントの数。新しいドキュメントが作成された場合も1を返します。
        """
        collection = self.db[collection_name]
        result = collection.update_one({}, {'$push': {field_name: data}}, upsert=True)
        return result.modified_count

    def get_unique_collection_name(self):
        """
        データベース内で一意のコレクション名を生成します。

        UUIDを使用して一意の識別子を生成し、それがデータベース内の既存のコレクション名と衝突しないことを確認します。
        
        Returns:
        str: 生成された一意のコレクション名。
        """
        unique_name = datetime.now().strftime('%Y%m%d%H%M%S')
        if unique_name not in self.db.list_collection_names():
            self.collection = self.db[unique_name]
            return unique_name
    
    def print_collection(self, collection_name):
        collection = self.db[collection_name]
        documents = collection.find()
        for document in documents:
            pprint.pprint(document)

    
    def print_all_tables(self, now_id, keys):
        """
        データベース内の指定されたIDのコレクションからデータを取得し、指定されたキーに基づいてそれらを表形式で表示します。

        Parameters:
        now_id (ObjectId): 取得したいドキュメントのID。
        keys (list): 表示したい列のキー（フィールド名）のリスト。
        """
        # IDに一致するドキュメントを取得
        collection = self.db[str(now_id)]
        document = collection.find_one({'_id': now_id})

        # データが空でないことを確認
        if document:
            # データを指定されたキーのみを含むようにフィルタリング
            filtered_data = []
            for key in keys:
                value = document.get(key, None)
                if isinstance(value, list):
                    # リストの場合、その各要素を並べる
                    value = " ".join(map(str, value))
                filtered_data.append(value)
            
            # DataFrameで表示
            df = pd.DataFrame([filtered_data], columns=keys)
            print(df.to_string(index=False))
        else:
            print("No data found in the database.")

def check_db_exists(db_name):
        # MongoDBに接続
    client = MongoClient('mongodb://localhost:27017/')
        
    # 現在のデータベース一覧を取得
    db_list = client.list_database_names()
    
    # 指定したデータベース名が一覧に存在するか確認
    return db_name in db_list