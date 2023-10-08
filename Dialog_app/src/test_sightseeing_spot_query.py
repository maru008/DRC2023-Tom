from pymongo import MongoClient

def build_query(base_criteria, lgenre):
    criteria = base_criteria.copy()
    criteria["LGenre"] = [lgenre]
    
    query = {}
    
    if "LGenre" in criteria and criteria["LGenre"]:
        query["GenreList.LGenre.Name"] = {"$in": criteria["LGenre"]}
        
    if "MGenre" in criteria and criteria["MGenre"]:
        query["GenreList.MGenre.Name"] = {"$in": criteria["MGenre"]}
        
    if "Genre" in criteria and criteria["Genre"]:
        query["GenreList.Genre.Name"] = {"$in": criteria["Genre"]}
        
    if "SightOption" in criteria and criteria["SightOption"]:
        query["SightOptionList.SightOptionName"] = {"$in": criteria["SightOption"]}
        
    return query

def fetch_sight_data(criteria):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Sightseeing_Spot_DB']
    collection = db['sightseeing_spots']

    sight_data = {}
    
    for lgenre in criteria["LGenre"]:
        query = build_query(criteria, lgenre)
        results = collection.find(query)
        
        # 重複を排除
        seen_ids = set()
        distinct_results = []
        for result in results:
            if result["SightID"] not in seen_ids:
                seen_ids.add(result["SightID"])
                distinct_results.append(result)
        
        sight_data[lgenre] = [{"SightID": item["SightID"], "Title": item["Title"]} for item in distinct_results]
    
    return sight_data

def print_sight_data(data):
    for lgenre, sights in data.items():
        print(f"LGenre: {lgenre}")
        for sight in sights:
            print(f"SightID: {sight['SightID']}, Title: {sight['Title']}")
        print("----------")

# 使用例
criteria = {'LGenre': ['食べる', '見る'], 'MGenre': ['和食', 'その他', '社寺・教会'], 'Genre': ['和食・日本料理', 'その他体験施設', '社寺・教会'], 'SightOption': ['夏におすすめ', ''], 'Time': [''], 'DayOfTheWeek': [''], 'Traffic': ['']}

sight_data = fetch_sight_data(criteria)
print_sight_data(sight_data)
