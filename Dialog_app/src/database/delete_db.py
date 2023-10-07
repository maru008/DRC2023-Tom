from mongo_tools import MongoDB

mongodb = MongoDB('Dialog_system') #クラス呼び出し

print(f"{'Dialog_system'}のデータベースを全て削除します．本当によろしいですか？")
ans = input("y/n:")
if ans == "y":
    mongodb.reset_database()
