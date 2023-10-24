
def judge_roop_break(resulting_sight_id_mtx,Dialog_turn_num,start_time,current_time):
    """
    最初の質問応答ループの抜ける条件
    ・対話ターンが5以上 (早く終わらないように)
    ・推薦できている観光地が多い
        ・
    ・時間が五分を終えらた強制終了
    
    出力
    ・True or False (Trueなら次のフェーズへ行く)
    """
    # 経過時間を計算
    elapsed_time = (current_time - start_time).seconds
    
    if elapsed_time > 5 * 60:#五分経ったら強制終了
        return True
    
    #対話が５ターン続いていて，観光地のカテゴリが1つ以上で,その中に4つ以上データがあればBreak
    if Dialog_turn_num >5 and len(resulting_sight_id_mtx) >= 1 and len(resulting_sight_id_mtx[0]) >= 4:
        return True
    
    return False 

def Judge_change_subject(resulting_sight_id_mtx,Dialog_turn_num):
    """
    話題変換するかどうかの判定処理
    出力
    ・True or False (Trueなら話題変換をする)
    """
    # 対話ターンが4の倍数の時で，resulting_sight_id_mtxがまだ１件しか取れてない場合
    if Dialog_turn_num % 4 == 0 and len(resulting_sight_id_mtx) <= 1:
        return True
    return False