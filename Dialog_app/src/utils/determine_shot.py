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
    # 配列が空か、全ての要素が3つ以下の場合
    if not data or sum(len(row) for row in data) < 4:
        return None

    selected_elements = []

    # 配列の行が2つ以上ある場合、それぞれの行から要素を選ぶ
    if len(data) > 1:
        for row in data:
            if len(selected_elements) < 4:
                selected_elements.append(random.choice(row))
            else:
                break

        # 選ばれた要素が4つに達していない場合、必要な数だけ追加で選ぶ
        while len(selected_elements) < 4:
            # 全ての行の要素を一つのリストに平坦化
            flat_list = [item for sublist in data for item in sublist]
            # 重複を避けるために、既に選択されている要素をリストから取り除く
            for element in selected_elements:
                if element in flat_list:
                    flat_list.remove(element)

            if flat_list:  # まだ選べる要素がある場合
                selected_elements.append(random.choice(flat_list))
            else:  # 選べる要素がない場合
                return None

    # 配列の行が1つしかない場合、その中から4つランダムに選ぶ
    else:
        if len(data[0]) >= 4:
            selected_elements = random.sample(data[0], 4)
        else:
            return None

    return selected_elements
