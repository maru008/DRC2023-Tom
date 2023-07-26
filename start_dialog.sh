#!/bin/bash
docker-compose up -d db
docker-compose up -d nlu_server_app
read -p "コマンド対話モードを実行しますか (y/n)? " interactive_mode
docker-compose run --rm dialog_app python src/main.py $interactive_mode