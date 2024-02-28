# 旅行代理店対話ロボットシステム (in DRC2023)
in DRC2023, Team Tom
# 概要
２つのLLMを非同期的に動かし，対話を行うシステムです．
詳細は[こちら](https://arxiv.org/abs/2312.13925)の論文に記述されています．

# 提案システム
非同期的に対話進行を行う Dual Large Language Model for Dialog system アーキテクチャ
<img width="665" alt="image" src="https://github.com/maru008/DRC2023-Tom/assets/51712520/fec49335-9072-4b87-8147-6a2c9a549967">

# 実行
## 環境
- Python
- Docker
  
### 環境設定
対話メインプログラムはpythonを用います．
仮想環境を作成

```
python -m venv .venv 
```

仮想環境に入ってライブラリをインストール
```
source .venv/bin/activate
pip install -r Dialog_app/requirements.txt
```
Windows系であれば以下
```
.venv\Scripts\activate
python -m pip install -r Dialog_app/requirements.txt
```

---
## 設定項目
APIキーやサーバホストを各自の設定ファイルに作成する．APIは以下が必要です．
- OpenAI
- RURUBU
- Google
- NAVITIME
  
以下のパスのようにconfig.iniファイルを作成する．
- config.ini

形式は以下.(適宜変更する)

```
[API_Key]
OpenAI = *************
RURUBU = *************
GOOGLE = *************
NAVITIME = *************

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
## 観光地データベースの準備
地理データを準備する必要があります．
具体的には以下のデータ処理を行います．

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

コマンド対話モードを使用しますか？(y/n)を聞かれるので，会話だけをしたい時はy．
対話関連のサーバに接続をして試したい時はnを入力する．
