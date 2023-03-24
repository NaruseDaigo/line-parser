import re
import pandas as pd 
from wordcloud import WordCloud


def create_wordcloud(talk_history, friend_name, num):
    my_lines = "\n".join(talk_history.query(f"flag == 10 and 発言者 == '{MY_NAME}'")["内容"])
    fr_lines = "\n".join(talk_history.query(f"flag == 10 and 発言者 == '{friend_name}'")["内容"])
    
    my_words = parse_str(my_lines)
    friend_words = parse_str(fr_lines)

    stop_words =  open("MySlothLib.txt", encoding="utf8").readlines()
    for i,  w in enumerate(stop_words):
        stop_words[i] = w.rstrip('\n')
    mylist = ["URL", "笑", "笑笑", "通話", "時間", "今日", "明日", "ん", "の", "する", "ある", "やる", "いい", "こと", "そう", "それ", "おれ", "なん", "俺", "オレ", "これ", "http", "https"]
    stop_words.extend(mylist)

    my_wc = WordCloud(max_font_size=100, \
                   background_color="white", \
                   stopwords=set(stop_words), \
                   width=400, height=400, \
                   font_path=FONT_PATH).generate(my_words)
    fr_wc = WordCloud(max_font_size=100, \
                   background_color="white", \
                   stopwords=set(stop_words), \
                   width=400, height=400, \
                   font_path=FONT_PATH).generate(friend_words)
    all_wc = WordCloud(max_font_size=100, \
                   background_color="white", \
                   stopwords=set(stop_words), \
                   width=400, height=400, \
                   font_path=FONT_PATH).generate(my_words + friend_words)

    my_wc.to_file(f"./png/{str(num).zfill(2)}{MY_NAME}_to_{friend_name}.png")
    fr_wc.to_file(f"./png/{str(num).zfill(2)}{friend_name}_to_{MY_NAME}.png")
    all_wc.to_file(f"./png/{str(num).zfill(2)}{friend_name}_and_{MY_NAME}.png")