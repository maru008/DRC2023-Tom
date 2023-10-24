from database.mongodb_tools_Dialog import MongoDB

Dialog_mongodb = MongoDB('DRC2023_Dialog_DB')

collection_name = '2023_10_24_15_22_04'

update_json = {
    "User_going_spot":["伏見稲荷","データベース"]
}

Dialog_mongodb.update_data(collection_name,update_json)