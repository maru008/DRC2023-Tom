import random

all_LGenre = ['見る', '食べる', '遊ぶ', '温泉地', '喫茶・甘味', '買う']

change_subject_text = {
    '見る':'ところで何かみたい観光地などありますでしょうか',
    '食べる':'ところで，何か食べたいものなどありますか？京都にはいろいろ名所がありますよ',
    '遊ぶ':'ところで，遊ぶスポットなどどうでしょう．京都にはいろいろありますよ',
    '喫茶・甘味':'ところで喫茶店など興味ありますか？',
    '買う':'ところで，何か買うことに興味あったりしますか？',
    '温泉地':'ところで，リラックスできる温泉などに興味あったりしますか？',
}

def change_subject(now_json):
    now_LGenre = now_json["LGenre"]
    trg_LGenre = list(set(all_LGenre)- set(now_LGenre))
    selected_LGenre = random.choice(trg_LGenre)
    rtn_text = change_subject_text[selected_LGenre]
    return rtn_text


def select4spot(data):

    # 最終的に選ばれる要素のリスト
    selected_elements = []

    # 行が4つ以上あるかどうかをチェック
    if len(data) >= 4:
        # ランダムに4行を選ぶ
        rows = random.sample(data, 4)
    else:
        # 4つ未満の場合は、全ての行を使用
        rows = data * (4//len(data)) + random.sample(data, 4%len(data))

    for row in rows:
        while True:
            # 各行からランダムに1つの要素を選ぶ
            element = random.choice(row)
            if element not in selected_elements:
                # 同じ数値がない場合のみ、リストに追加する
                selected_elements.append(element)
                break  # 次の行に進む

    return selected_elements
