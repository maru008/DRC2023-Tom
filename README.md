# 旅行代理店対話ロボットシステム (in DRC2023)
in DRC2023, Team Tom

## 環境
- Python
- Docker
### 環境設定
対話メインプログラムはpythonを用います．
仮想環境を作成することを推奨．
```
python -m venv .venv #.venvにすることでgitにコミットされない
```

仮想環境に入る
```
source .venv/bin/activate
```
対話プログラム（start_dialog.sh）は以降この環境で実行．
---
## 設定項目
APIキーやサーバホストを各自の設定ファイルに作成する．
以下のパスのようにconfig.iniファイルを作成する．
- config.ini
  
形式は以下.(適宜変更する)
```
[API_Key]
OpenAI = *************
RURUBU = *************

[Server_Info]
Server_ip = 192.168.2.213
SpeechRecognition_port = 8888
SpeechGenerator_port = 3456
RobotExpressionController_port = 20000
RobotBodyController_port = 21000
FaceRecognition_port = 4500
```

実行は以下のシェルファイルを実行する．
- start_server.sh
- start_dialog.sh
  
コマンド対話モードを使用しますか？(y/n)を聞かれるので，会話だけをしたい時はy．サーバ接続をして試したい時はnを入力する．

---
## フォルダ構成
このプロジェクトは以下の構成で作成されている．
```
.
├── Dialog_app
│   ├── requirements.txt
│   └── src
│       ├── DialogModules
│       │   ├── NLGModule.py
│       │   └── Prompts
│       │       └── Dialog_staff.txt
│       ├── ServerModules
│       │   ├── expression_generation.py
│       │   ├── motion_generation.py
│       │   ├── speech_generation.py
│       │   └── voice_recognition.py
│       ├── database
│       │   └── mongo_tools.py
│       ├── main.py
│       └── utils
│           ├── TCPserver.py
│           ├── config_reader.py
│           └── general_tool.py
├── LICENSE
├── MongoDB
│   ├──...
│
├── NLUServer_app
│   ├── Dockerfile
│   ├── config.ini
│   ├── requirements.txt
│   └── src
│       ├── NLUModule
│       │   ├── Prompts
│       │   │   └── GPT4_NLU.txt
│       │   ├── Text_NLU_module.py
│       │   └── __pycache__
│       │       └── Text_NLU_module.cpython-39.pyc
│       ├── main.py
│       └── utils
│           ├── config_reader.py
│           ├── mongodb_tool.py
│           └── receive_data.py
├── README.md
├── config.ini
├── docker-compose.yml
├── start_dialog.sh
└── start_server.sh
```
