import datetime

def SectionPrint(text):
    print("="*100)
    print(text)
    print("="*100)
    
def check_time_exceeded(start_time, threshold_minutes=10, function_to_run=None):
    # 関数を実行
    if function_to_run is not None:
        function_to_run()

    # 現在の時間を取得
    end_time = datetime.datetime.now()

    # 経過時間を計算（秒）
    elapsed_seconds = (end_time - start_time).seconds

    # 経過時間を分と秒に変換
    elapsed_minutes = elapsed_seconds // 60
    remaining_seconds = elapsed_seconds % 60

    # 経過時間をフォーマットして出力
    formatted_time = f'{elapsed_minutes:02d}:{remaining_seconds:02d}'
    print(f'Time> {formatted_time}')

    # 基準時間を超えたかどうかをチェック
    exceeded = elapsed_minutes >= threshold_minutes

    return exceeded
