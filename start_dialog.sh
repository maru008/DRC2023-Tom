#!/bin/bash

# Dockerコンテナをバックグラウンドで立ち上げる
docker-compose up -d

# 対話アプリのディレクトリに移動
cd ./Dialog_app

# virtualenvが存在することを確認
if [ -f "../.venv/bin/activate" ]; then
  # virtualenvをアクティベート
  source ../.venv/bin/activate

  # ユーザーに対話モードを問い合わせ
  # read -p "コマンド対話モードを実行しますか (y/n)? " interactive_mode

  # Pythonスクリプトを実行
  # python src/main.py $interactive_mode
  python src/main.py
  # virtualenvをデアクティベート
  deactivate
else
  echo "エラー: virtualenvが見つかりません。'.venv/bin/activate'が存在することを確認してください。"
fi
