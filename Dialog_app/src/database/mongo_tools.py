# mongo_tools.py
import uuid
from pymongo import MongoClient
from tabulate import tabulate

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
        while True:
            unique_id = str(uuid.uuid4())
            if unique_id not in self.db.list_collection_names():
                return unique_id


    def print_all_tables(self, keys):
        """
        データベース内の全てのコレクションからデータを取得し、指定されたキーに基づいてそれらを表形式で表示します。

        Parameters:
        keys (list): 表示したい列のキー（フィールド名）のリスト。
        """
        # データベース内の全てのコレクション名を取得
        all_collections = self.db.list_collection_names()

        # 全てのコレクションからデータを取得して1つのリストに結合
        all_data = []
        for collection_name in all_collections:
            collection = self.db[collection_name]
            documents = collection.find()
            
            # 全てのドキュメントをリストに変換
            data = [doc for doc in documents]
            all_data.extend(data)

        # データが空でないことを確認
        if all_data:
            # データを指定されたキーのみを含むようにフィルタリング
            filtered_data = []
            for doc in all_data:
                for key in keys:
                    if isinstance(doc.get(key), list):
                        for item in doc.get(key):
                            new_doc = {k: doc.get(k, None) if k != key else item for k in keys}
                            filtered_data.append(new_doc)
                    else:
                        new_doc = {k: doc.get(k, None) for k in keys}
                        filtered_data.append(new_doc)

            table = tabulate(filtered_data, headers="keys", tablefmt="grid")
            print(table)
        else:
            print("No data found in the database.")
