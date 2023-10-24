# 旅行代理店対話ロボットシステム (in DRC2023)
in DRC2023, Team Tom

## 環境
- Python
- Docker
- Unix系(mac or Ubuntu)
  
### 環境設定
対話メインプログラムはpythonを用います．
仮想環境を作成することを推奨．
```
python -m venv .venv #.venvにすることでgitにコミットされない
```

仮想環境に入ってライブラリをインストール
```
source .venv/bin/activate
pip install -r Dialog_app/requirements.txt
```
または
```
.venv\Scripts\activate
python -m pip install -r Dialog_app/requirements.txt
```
対話プログラム（start_dialog.sh）は以降この環境で実行．
---
## 設定項目
APIキーやサーバホストを各自の設定ファイルに作成する．APIは以下が必要です．
- OpenAI
- RURUBU
- Google
  
以下のパスのようにconfig.iniファイルを作成する．
- config.ini

形式は以下.(適宜変更する)

```
[API_Key]
OpenAI = *************
RURUBU = *************
GOOGLE = *************

[Server_Info]
Server_ip = 172.22.137.149
SpeechRecognition_port = 8888
SpeechGenerator_port = 3456
RobotExpressionController_port = 20000
RobotBodyController_port = 21000
FaceRecognition_port = 4500
SiteViewer_port = 25000
```

---
## 前準備
地理データを準備する必要があります．
具体的には以下のデータ処理を行います．

```
python CityGraph_app/src/data_preparation.py
```

---
## 実行方法
実行は以下のファイルを実行する．
mac or linux環境
```
start_dialog.sh
```
Windows環境
```
start_dialog.bat
```

コマンド対話モードを使用しますか？(y/n)を聞かれるので，会話だけをしたい時はy．サーバ接続をして試したい時はnを入力する．
