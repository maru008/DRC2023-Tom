@echo off
docker-compose up -d
cd Dialog_app
if exist "..\.venv\Scripts\activate.bat" (
    call ..\.venv\Scripts\activate.bat
    set /p interactive_mode="コマンド対話モードを実行しますか (y/n)? "
    python src\main.py %interactive_mode%
    deactivate
) else (
    echo エラー: virtualenvが見つかりません。'.venv\Scripts\activate.bat'が存在することを確認してください。
)
