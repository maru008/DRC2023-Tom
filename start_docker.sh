#!/bin/bash
read -p "コマンド対話モードを実行しますか (y/n)? " interactive_mode
docker-compose run --rm app python main.py $interactive_mode
