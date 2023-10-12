import json
from database.mongodb_tools_Sightseeing import SightseeingDBHandler, generate_combinations

Sightseeing_mongodb = SightseeingDBHandler("Sightseeing_Spot_DB")
print("単体実験===============================================================")
sight_ids_by_lgenre = Sightseeing_mongodb.get_sight_ids_by_lgenre("食べる")
sight_ids_by_mgenre = Sightseeing_mongodb.get_sight_ids_by_mgenre("和食")
sight_ids_by_genre = Sightseeing_mongodb.get_sight_ids_by_genre("和食・日本料理")
sight_ids_by_sight_option_name = Sightseeing_mongodb.get_sight_ids_by_sight_option_name("女子おすすめ")

print(len(sight_ids_by_lgenre))
print(len(sight_ids_by_mgenre))
print(len(sight_ids_by_genre))
print(len(sight_ids_by_sight_option_name))
print("単体JSON実験===============================================================")
conditions_json = json.dumps({
    "LGenre": "食べる",
    "MGenre": "社寺・教会",
    "Genre": "和食・日本料理",
})
common_sight_ids = Sightseeing_mongodb.get_sight_ids_by_multiple_conditions(conditions_json)

print(common_sight_ids)

print("複数JSON実験===============================================================")
input_conditions = {
    "LGenre": ["食べる", "見る"],
    "MGenre": ["社寺・教会", "自然"],
    "Genre": ["和食・日本料理", "山・丘陵"],
    "SightOption": []
}

# 可能なすべての組み合わせの生成
all_combinations = generate_combinations(input_conditions)

# 結果のIDのリストを保持するセット
resulting_sight_ids = set()

# データベースハンドラーのインスタンス化（実際のデータベース名を指定してください）

# すべての組み合わせに対してクエリを実行し、結果を集めます
for combination in all_combinations:
    print(combination)
    condition_json = json.dumps(combination)
    sight_ids = Sightseeing_mongodb.get_sight_ids_by_multiple_conditions(condition_json)
    print(len(sight_ids))
    resulting_sight_ids.update(sight_ids)  # セットにIDを追加（重複するIDは無視されます）

# 最終的なSightIDのリストを出力
print(list(resulting_sight_ids))