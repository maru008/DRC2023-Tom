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
                if random() < 1/916:
                    output_text += "$"
            if part_of_speech == "形容詞":
                if random() < 3/410:
                    output_text += "$"
            if part_of_speech == "名詞":
                if random() < 50/1312:
                    output_text += "$"
            if part_of_speech == "代名詞":
                if random() < 13/331:
                    output_text += "ー"
                if random() < 3/331:
                    output_text += "$"
                if random() < 2/331:
                    output_text += filler2
            if part_of_speech == "副詞":
                if random() < 35/508:
                    output_text += "ー"
                if random() < 13/508:
                    output_text += "$"
                if random() < 7/508:
                    output_text += filler2
                if random() < 7/508:
                    output_text += filler1
                if random() < 1/508:
                    output_text += filler3
            if part_of_speech == "連体詞":
                if random() < 22/63:
                    output_text += "ー"
            if part_of_speech == "接続詞":
                if random() < 9/83:
                    output_text += "$"
                if random() < 2/83:
                    output_text += filler2
                if random() < 1/83:
                    output_text += filler3
                if random() < 1/83:
                    output_text += filler4
            if part_of_speech == "助詞":
                if random() < 397/2454:
                    output_text += "ー"
                if random() < 61/2454:
                    output_text += "$"
                if random() < 23/2454:
                    output_text += filler2
                if random() < 1/2454:
                    output_text += filler3
                if random() < 4/2454:
                    output_text += filler4
                if random() < 9/2454:
                    output_text += filler1
                if random() < 2/2454:
                    output_text += filler3
            if part_of_speech == "助動詞":
                if random() < 1/1043:
                    output_text += "ー"
                if random() < 1/1043:
                    output_text += "$"
                if random() < 2/1043:
                    output_text += filler2
                if random() < 1/1043:
                    output_text += filler3
                if random() < 3/1043:
                    output_text += filler1
    return output_text
