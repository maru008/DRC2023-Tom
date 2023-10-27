import random
import pandas as pd
import copy

spot_all = pd.read_csv("../Sightseeing_Spot_data/data/output_data/value_count.csv")

spot_id_ls = spot_all[spot_all["Key"] == "SightID"]["Value"].to_list()
spot_id_ls = [int(spot_id_i) for spot_id_i in spot_id_ls]

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
    try:
        if len(data) == 0: #配列の長さが0の時は全てからランダムで
            spot4_ls = random.sample(spot_id_ls,4)
            return False, spot4_ls
        
        if len(data) == 1: #1行のみ存在する場合
            trg_spot_ls = data[0]
            if len(trg_spot_ls) < 4: 
                spot_num = len(trg_spot_ls)
                nokori_spot = 4 - spot_num
                return_spot_ls = copy.deepcopy(trg_spot_ls)
                return_spot_ls.extend(random.sample(spot_id_ls, nokori_spot))
                return True, return_spot_ls
            else:
                return True, random.sample(trg_spot_ls, 4)
        
        else: #2行以上存在する場合
            selected_rows = random.sample(data, min(4, len(data))) # 4行もしくは存在する行数だけランダムに選択
            return_spot_ls = []
            for row in selected_rows:
                return_spot_ls.append(random.choice(row))
                if len(return_spot_ls) == 4:
                    break
            while len(return_spot_ls) < 4: # 選択された要素が4未満の場合、残りを埋める
                return_spot_ls.append(random.choice(random.choice(data)))
            return True, return_spot_ls
    except:# すべての実行パスで値を返すようにするためのデフォルト返り値
        return False, random.sample(spot_id_ls,4)  

