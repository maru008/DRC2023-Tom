# 旅行代理店対話ロボットシステム (in DRC2023)
in DRC2023, Team Tom

## 環境
- Docker

---
## 設定項目
APIキーやサーバホストを各自の設定ファイルに作成する．
以下のパスのようにconf.iniファイルを作成する．
- conf.ini
  
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
- start_docker.sh
  
コマンド対話モードを使用しますか？(y/n)を聞かれるので，会話だけをしたい時はy．サーバ接続をして試したい時はnを入力する．

---
## フォルダ構成
このプロジェクトは以下の構成で作成されている．
```
.
├── Dockerfile
├── LICENSE
├── README.md
├── config.ini
├── docker-compose.yml
├── requirements.txt
├── src
│   ├── database                        #データベースに関するモジュール群
│   │   └── mongo_tools.py
│   ├── main.py
│   ├── modules                         #モジュール群
│   │   ├── expression_generation.py
│   │   ├── motion_generation.py
│   │   ├── speech_generation.py
│   │   └── voice_recognition.py
│   └── utils
│       └── config_reader.py
└── start_docker.sh                     #main.pyを実行するファイル
```
