from pymongo import MongoClient
import json
from collections import Counter
import itertools
from functools import reduce 

class SightseeingDBHandler:
    def __init__(self,db_name):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[db_name]
        self.collection = self.db["sightseeing_spots"]

    def get_sight_ids_by_lgenre(self, value):
        """
        LGenreに基づいてSightIDのリストを取得します。
        
        :param value: LGenreの値（例：'食べる'）
        :return: 該当するSightIDのリスト
        """
        results = self.collection.find({"GenreList.LGenre.Name": value}, {"SightID": 1, "_id": 0})
        sight_ids = [result["SightID"] for result in results]
        return sight_ids

    def get_sight_ids_by_mgenre(self, value):
        """
        MGenreに基づいてSightIDのリストを取得します。
        
        :param value: MGenreの値（例：'和食'）
        :return: 該当するSightIDのリスト
        """
        results = self.collection.find({"GenreList.MGenre.Name": value}, {"SightID": 1, "_id": 0})
        sight_ids = [result["SightID"] for result in results]
        return sight_ids

    def get_sight_ids_by_genre(self, value):
        """
        Genreに基づいてSightIDのリストを取得します。
        
        :param value: Genreの値（例：'和食・日本料理'）
        :return: 該当するSightIDのリスト
        """
        results = self.collection.find({"GenreList.Genre.Name": value}, {"SightID": 1, "_id": 0})
        sight_ids = [result["SightID"] for result in results]
        return sight_ids

    def get_sight_ids_by_sight_option_name(self, value):
        """
        SightOptionNameに基づいてSightIDのリストを取得します。
        
        :param value: SightOptionNameの値（例：'女子おすすめ'）
        :return: 該当するSightIDのリスト
        """
        results = self.collection.find({"SightOptionList.SightOptionName": value}, {"SightID": 1, "_id": 0})
        sight_ids = [result["SightID"] for result in results]
        return sight_ids
    
    def get_sight_ids_by_multiple_conditions(self, conditions_json):
        """
        複数の条件に基づいてSightIDのリストを取得します。

        :param conditions_json: 条件のJSON（例：'{"LGenre":"食べる", "MGenre":"社寺・教会", "Genre":"和食・日本料理", "SightOption":"女子おすすめ"}'）
        :return: 該当するSightIDのリスト
        """
        conditions = json.loads(conditions_json)
        sets_of_sight_ids = []  # IDのセットのリストを作成します。

        if "LGenre" in conditions:
            lgenre_ids = set(self.get_sight_ids_by_lgenre(conditions["LGenre"]))
            sets_of_sight_ids.append(lgenre_ids)
        if "MGenre" in conditions:
            mgenre_ids = set(self.get_sight_ids_by_mgenre(conditions["MGenre"]))
            sets_of_sight_ids.append(mgenre_ids)
        if "Genre" in conditions:
            genre_ids = set(self.get_sight_ids_by_genre(conditions["Genre"]))
            sets_of_sight_ids.append(genre_ids)
        if "SightOption" in conditions and conditions["SightOption"]:  # キーが存在し、値がある場合のみクエリを実行します。
            sight_option_ids = set(self.get_sight_ids_by_sight_option_name(conditions["SightOption"]))
            sets_of_sight_ids.append(sight_option_ids)

        # すべてのセットの和集合を取得します。reduce関数を使用してセットのリストを一つのセットにまとめます。
        common_sight_ids = set.intersection(*sets_of_sight_ids) if sets_of_sight_ids else set()

        return list(common_sight_ids)  # 最終結果をリストとして返します。
    
   
    def id2info_forView(self,SightID):
        data = self.collection.find_one({'SightID': SightID})
        # データから各情報を取得
        if data:
            title = data['Title']
            image_files = [photo.get('URL') for photo in data.get('PhotoList', []) if photo.get('URL') is not None]
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
            if (image_files is None) or len(image_files) == 0:
                res_json[f"ImageURL{i+1}"] = 'None'
            else:
                res_json[f"ImageURL{i+1}"] = f'https://www.j-jti.com/Storage/Image/Product/SightImage/Org/{image_files[0]}'
            res_json[f"MapURL{i+1}"] = f'https://www.google.co.jp/maps/@{latitude},{longitude},15z'
            res_json[f"Name{i+1}"] = title
        return res_json
    
    def get_summary_by_sight_id(self, sight_id):
        """
        指定されたSightIDに対応する観光地のサマリーを取得します。

        :param collection_name: クエリを実行するコレクションの名前
        :param sight_id: サマリーを取得する観光地のSightID
        :return: 観光地のサマリー(文字列)。該当するデータがない場合はNoneを返します。
        """
        result = self.collection.find_one({"SightID": sight_id}, {"_id": 0, "Summary": 1})

        if result:
            return result["Summary"]
        else:
            return None
    def get_title_by_sight_id(self, sight_id):
        """
        指定されたSightIDに対応する観光地のタイトルを取得します。

        :param sight_id: タイトルを取得する観光地のSightID
        :return: 観光地のタイトル（文字列）。該当するデータがない場合はNoneを返します。
        """
        result = self.collection.find_one({"SightID": sight_id}, {"_id": 0, "Title": 1})

        if result:
            return result["Title"]
        else:
            return None
    def get_coordinates_by_sight_id(self, sight_id):
        """
        指定されたSightIDに対応する観光地の緯度と経度を取得します。

        :param collection_name: クエリを実行するコレクションの名前
        :param sight_id: 緯度と経度を取得する観光地のSightID
        :return: 緯度と経度のリスト。該当するデータがない場合はNoneを返します。
        """
        result = self.collection.find_one({"SightID": sight_id}, {"_id": 0, "LatitudeW10": 1, "LongitudeW10": 1})

        if result and "LatitudeW10" in result and "LongitudeW10" in result:
            # 緯度と経度をfloat型に変換してから返す
            return float(result["LatitudeW10"]), float(result["LongitudeW10"])
        else:
            return None
          
def generate_combinations(conditions):
    # 空のリストを持つキーを削除する
    conditions = {key: val for key, val in conditions.items() if val}

    keys = conditions.keys()
    values = (conditions[key] for key in keys)
    combinations = [dict(zip(keys, combination)) for combination in itertools.product(*values)]

    return combinations

