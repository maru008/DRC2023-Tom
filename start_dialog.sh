#!/bin/bash
cd ./Dialog_app
read -p "コマンド対話モードを実行しますか (y/n)? " interactive_mode
python src/main.py $interactive_mode