from pymongo import MongoClient

def build_query(criteria):
    query = {}
    
    # LGenreに関するクエリの追加
    if "LGenre" in criteria and criteria["LGenre"]:
        query["GenreList.LGenre.Name"] = {"$in": criteria["LGenre"]}
        
    # MGenreに関するクエリの追加
    if "MGenre" in criteria and criteria["MGenre"]:
        query["GenreList.MGenre.Name"] = {"$in": criteria["MGenre"]}
        
    # Genreに関するクエリの追加
    if "Genre" in criteria and criteria["Genre"]:
        query["GenreList.Genre.Name"] = {"$in": criteria["Genre"]}
        
    # SightOptionに関するクエリの追加
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

# MongoDBサーバーへの接続

def fetch_sight_ids_titles(criteria):
    # MongoDBサーバへの接続設定
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Sightseeing_Spot_DB']
    collection = db['sightseeing_spots']
    
    # クエリの生成
    query = build_query(criteria)
    
    # クエリの実行
    results = collection.find(query, {"SightID": 1, "_id": 0})
    
    # SightIDのリストの作成
    sight_ids = [result['SightID'] for result in results]
    
    return sight_ids
# 使用例
criteria = {
    "LGenre": ["食べる"],
    "MGenre": ["和食"],
    "Genre": ["和食・日本料理"],
    "SightOption": ["夏におすすめ"],
    "Time": [""],
    "Traffic": [""]
}

result_data = fetch_sight_ids_titles(criteria)
print(result_data)