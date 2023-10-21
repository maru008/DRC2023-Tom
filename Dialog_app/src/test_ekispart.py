import requests
from utils.config_reader import read_config

config = read_config()


ACCESS_KEY = config.get("API_Key","EKISPERT")
ENDPOINT = 'https://api.ekispert.jp/v1/json/search/course/extreme?key=LE_cXwxgmjBdTTMq&viaList=22671:22741'

# リクエストパラメータ
params = {
    'key': ACCESS_KEY
}

def check_access_key():
    # APIにGETリクエストを送る
    response = requests.get(ENDPOINT)

    # レスポンスのステータスコードを確認
    if response.status_code == 200:
        print('アクセスキーは有効です。')
        print('レスポンスデータ:', response.text)
    elif response.status_code == 403:
        print('認証エラー: アクセスキーが無効か、ドメインが間違っています。')
    else:
        print(f'予期しないエラーが発生しました: {response.status_code}')

if __name__ == "__main__":
    check_access_key()
