#!/bin/bash
docker-compose up -d 
read -p "コマンド対話モードを実行しますか (y/n)? " interactive_mode
docker-compose exec dialog_app python ./src/main.py $interactive_mode  
