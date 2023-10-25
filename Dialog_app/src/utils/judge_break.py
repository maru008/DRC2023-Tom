
def Judge_roop_break(resulting_sight_id_mtx,Dialog_turn_num,start_time,current_time):
    """
    この関数は、対話の状態に基づいて、ループを抜けるかどうかを判断します。
    以下の条件のいずれかがTrueの場合、この関数はTrueを返します：

    1. 経過時間が300秒を超える場合 (5分を超える場合)。
    2. 対話のターン数が5を超え、推薦される観光地のカテゴリーが1つ以上存在し、
       かつそのカテゴリーに4つ以上の観光地が含まれる場合。

    変数の説明:
    - 経過時間 (elapsed_time) は、現在の時間 (current_time) から開始時間 (start_time) を差し引いたものです。
    - 対話のターン数 (Dialog_turn_num) は、対話が開始されてからのターンの総数です。
    - resulting_sight_id_mtx は、推薦される観光地のカテゴリーを含むリストです。
      このリストのサイズ (len(resulting_sight_id_mtx)) がカテゴリーの数を示します。
      各カテゴリーの観光地の数は、そのカテゴリーのリストの長さ (例: len(resulting_sight_id_mtx[0])) によって示されます。

    返り値:
    - True または False。Trueが返された場合、対話は次のフェーズに進みます。
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