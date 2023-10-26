import random

all_LGenre = ['見る', '遊ぶ', '温泉地']

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
    # 配列が空か、全ての要素が3つ以下の場合
    if not data or sum(len(row) for row in data) < 4:
        return None

    selected_elements = []
    flat_list = [item for sublist in data for item in sublist]

    # 配列の行が2つ以上ある場合、それぞれの行から要素を選ぶ
    if len(data) > 1:
        for row in data:
            unique_row = [item for item in row if item not in selected_elements]
            if unique_row:  # 重複しない要素があれば
                choice = random.choice(unique_row)
                selected_elements.append(choice)
                flat_list.remove(choice)  # 選択された要素をflat_listから除外
            if len(selected_elements) == 4:  # 4つ選択できたら終了
                return selected_elements

        # 選ばれた要素が4つに達していない場合、必要な数だけ追加で選ぶ
        while len(selected_elements) < 4 and flat_list:
            choice = random.choice(flat_list)
            if choice not in selected_elements:  # 選択した要素が重複しないことを確認
                selected_elements.append(choice)
                flat_list.remove(choice)  # 選択された要素をflat_listから除外

            # 4つ選べたかどうかを確認
        if len(selected_elements) < 4:
            return None