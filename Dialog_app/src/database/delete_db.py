from mongodb_tools_Dialog import MongoDB

trg_db_name = input("削除対象のDB: ")
mongodb = MongoDB(trg_db_name) #クラス呼び出し

print(f"{trg_db_name}のデータベースを全て削除します．本当によろしいですか？")
ans = input("y/n:")
if ans == "y":
    mongodb.reset_database()
    print("データベースを削除しました.")
