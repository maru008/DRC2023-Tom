from sudachipy import dictionary
from random import random

def add_hesitation(text):
    # Tokenizerの初期化
    tokenizer_obj = dictionary.Dictionary().create()
    tokens = tokenizer_obj.tokenize(text)
    output_text = ""
    filler1 = "、えーっと、"
    filler2 = "、あのー、"
    filler3 = "、んー、"
    filler4 = "、そのー、"

    # 文章の先頭にフィラーを挿入
    if random() < 15/100:
        output_text += filler1
    if random() < 10/100:
        output_text += filler2
    if random() < 5/100:
        output_text += filler3
    if random() < 10/100:
        output_text += filler4
    
    for i, token in enumerate(tokens):
            surface = token.surface()  # 表層形
            part_of_speech = token.part_of_speech()[0]  # 品詞名

            output_text += surface

            if part_of_speech == "動詞":
                if random() < 432/64006:
                    output_text += "$"
            if part_of_speech == "形容詞":
                if random() < 204/18207:
                    output_text += "$"
            if part_of_speech == "代名詞":
                if random() < 497/21010:
                    output_text += ":"
                if random() < 359/21010:
                    output_text += "$"
                if random() < 357/21010:
                    output_text += filler2
            if part_of_speech == "副詞":
                if random() < 982/32868:
                    output_text += ":"
                if random() < 1421/32868:
                    output_text += "$"
                #  最後のトークンの場合にフィラーを追加しない
                if i < len(tokens) - 1:
                    if random() < 7/508:
                        output_text += filler2
                    if random() < 7/508:
                        output_text += filler1
                    if random() < 1/508:
                        output_text += filler3
            if part_of_speech == "連体詞":
                if random() < 2020/6084:
                    output_text += ":"
                if random() < 157/6084:
                    output_text += "$"
            if part_of_speech == "接続詞":
                if random() < 571/3777:
                    output_text += ":"
                if random() < 98/3777:
                    output_text += "$"
                if random() < 2/83:
                    output_text += filler2
                if random() < 1/83:
                    output_text += filler3
                if random() < 1/83:
                    output_text += filler4
            if part_of_speech == "助詞":
                if random() < 17667/179067:
                    output_text += ":"
                if random() < 7810/179067:
                    output_text += "$"
                if i < len(tokens) - 1:
                    if random() < 13/2454:
                        output_text += filler2
                    if random() < 1/2454:
                        output_text += filler3
                    if random() < 4/2454:
                        output_text += filler4
                    if random() < 9/2454:
                        output_text += filler1
            if part_of_speech == "助動詞":
                if random() < 1/1043:
                    output_text += ":"
                if random() < 1/1043:
                    output_text += "$"

    return output_text
