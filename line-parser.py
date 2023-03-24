import time
import re
import pandas as pd 
import MeCab

FONT_PATH = "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc"
MY_NAME = "成瀬 大悟"

def parse_str(input_string):
    mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    lines = mecab.parse(input_string).split('\n')[0:-2]
    words = []
    
    for line in lines:
        tmp = re.split('\t|,', line)
        if tmp[1] in ["名詞"]:
            words.append(tmp[7])  # 0: 表層形, 7: 原形
    
    return " ".join(words)


def cleanse_txt(talk_txt):
    p_url = re.compile(r"https?:\/\/[\w:%#\$&\?\(\)~\.=\+\-\/@]+")
    cleansed_talk_txt = []
    for i in talk_txt:
        cleansed_talk_txt.append(p_url.sub('[URL]', i))
    
    return cleansed_talk_txt

def parse_talk_history(cleansed_talk_txt):
    title = cleansed_talk_txt[0].rstrip("\n")
    save_date = cleansed_talk_txt[1].rstrip("\n")
    talk_data = cleansed_talk_txt[3:]

    # 宣言が下の正規表現ほど制約が緩いので、if分岐の順番に注意すること(p: pattern)
    ## 大分類6つ
    p_date = re.compile(r"^(\d{4}\/\d{2}\/\d{2}\((月|火|水|木|金|土|日)\))\n$")
    p_delete_msg1 = re.compile(r"^(\d{2}:\d{2})\t([\w\s\.]+)がメッセージの送信を取り消しました\n$")  # 相手が取り消した場合
    p_delete_msg2 = re.compile(r"^(\d{2}:\d{2})\tメッセージの送信を取り消しました\n$")  # 自分が取り消した場合
    p_time_and_msg = re.compile(r'^(\d{2}:\d{2})\t([\w\s\.]+)\t"?(.+)\n$')  # 改行のあるメッセージは"で囲まれている
    p_msg_only = re.compile(r'^(.+)"?\n$')  # 改行のあるメッセージの最終文は"で終わるが、途中文には"がない
    p_br  = re.compile(r"^\n$")

    ## p_time_and_msg中の分類
    p_change_group_name = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)がグループ名を「(.+)」に変更しました")
    p_video = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(\[動画\])")
    p_photo = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(\[写真\])")
    p_stamp = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(\[スタンプ\])")
    p_address = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(\[連絡先\])")
    p_file = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(\[ファイル\])")
    p_create_and_add_album = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(\[アルバム\])")
    p_add_album = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(\[アルバム\])")
    p_create_album = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(\[アルバム\])")
    p_create_group = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(\[グループ\])")
    p_add_group = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(\[グループ\])")
    p_create_and_add_group = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(\[グループ\])")
    p_call_system_messages = re.compile(r"\d{2}:\d{2}\t[\w\s\.]+\t☎ ") 
    
    ### p_call_system_messages中の分類
    p_call = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(☎ 通話時間 (\d\d?:){1,3}\d\d)")
    p_missed_call = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(☎ 不在着信)\n")
    p_canceled_call = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(☎ 通話をキャンセルしました)")
    p_no_answer_call = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(☎ 通話に応答がありませんでした)")
    p_invited_call = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(☎ グループ音声通話に招待されました。)")
    p_transfer_error = re.compile(r"(\d{2}:\d{2})\t([\w\s\.]+)\t(ⓘ このメッセージは、利用していた端末から移行されなかったため表示できません。)")
    
    # flag
    # -1 : saved data
    # 10 : talk message
    # 11 : delete message 相手が取り消した場合
    # 12 : delete message 自分が取り消した場合
    # 20 : stamp
    # 21 : photo
    # 22 : video
    # 23 : address
    # 30 : call
    # 31 : missed call 不在着信
    # 32 : canceled call 通話をキャンセルしました
    # 33 : no answer call 通話に応答がありませんでした
    # 34 : invited call ☎ グループ音声通話に招待されました。
    # 50 : system message unsent
    # 51 : transfer_error
    # 60 : file
    # 70 : create and add album
    # 71 : changed the name of the album
    # 72 : deleted the album
    
    talk_history_list = []
    date = time = name = msg = ""
    flag = -1
    max_i = len(talk_data)

    for i, line in enumerate(talk_data):
        if p_date.match(line):
            if flag == -1:
                pass
            else:
                talk_history_list.append([date, time, name, msg, flag])
                flag = -1
                
            date = p_date.match(line).groups()[0]
        elif p_delete_msg1.match(line):
            if flag == -1:
                pass
            else:
                talk_history_list.append([date, time, name, msg, flag])
                flag = -1
            flag = 11
            tmp = p_delete_msg1.match(line).groups()
            time = tmp[0]
            name = tmp[1]
            msg = "メッセージの送信を取り消しました"
        elif p_delete_msg2.match(line):
            if flag == -1:
                pass
            else:
                talk_history_list.append([date, time, name, msg, flag])
                flag = -1
            flag = 12
            tmp = p_delete_msg2.match(line).groups()
            time = tmp[0]
            name = MY_NAME
            msg = "メッセージの送信を取り消しました"
        elif p_msg.match(line):
            if flag == -1:
                pass
            else:
                talk_history_list.append([date, time, name, msg, flag])
                flag = -1
        
            if p_stamp.match(line):
                flag = 20
                tmp = p_stamp.match(line).groups()
                time = tmp[0]
                name = tmp[1]
                msg = tmp[2]
            elif p_photo.match(line):
                flag = 21
                tmp = p_photo.match(line).groups()
                time = tmp[0]
                name = tmp[1]
                msg = tmp[2]
            elif p_video.match(line):
                flag = 22
                tmp = p_video.match(line).groups()
                time = tmp[0]
                name = tmp[1]
                msg = tmp[2]
            elif p_address.match(line):
                flag = 23
                tmp = p_address.match(line).groups()
                time = tmp[0]
                name = tmp[1]
                msg = tmp[2]
            elif p_call_system_messages.match(line):
                if p_call.match(line):
                    flag = 30
                    tmp = p_call.match(line).groups()
                    time = tmp[0]
                    name = tmp[1]
                    msg = tmp[2]
                elif p_missed_call.match(line):
                    flag = 31
                    tmp = p_missed_call.match(line).groups()
                    time = tmp[0]
                    name = tmp[1]
                    msg = tmp[2]
                elif p_canceled_call.match(line):
                    flag = 32
                    tmp = p_canceled_call.match(line).groups()
                    time = tmp[0]
                    name = tmp[1]
                    msg = tmp[2]
                elif p_no_answer_call.match(line):
                    flag = 33
                    tmp = p_no_answer_call.match(line).groups()
                    time = tmp[0]
                    name = tmp[1]
                    msg = tmp[2]
                elif p_invited_call.match(line):
                    flag = 34
                    tmp = p_invited_call.match(line).groups()
                    time = tmp[0]
                    name = tmp[1]
                    msg = tmp[2]
                else:
                    print("error in calls")
                    print(line)
            elif p_transfer_error.match(line):
                flag = 51
                tmp = p_transfer_error.match(line).groups()
                time = tmp[0]
                name = tmp[1]
                msg = tmp[2]
            elif p_msg.match(line):
                flag = 10
                tmp = p_msg.match(line).groups()
                time = tmp[0]
                name = tmp[1]
                msg = tmp[2]
            else:
                print("error in msgs")
        elif p_textonly.match(line):
            msg += '\n'
            msg += p_textonly.match(line).groups()[0].rstrip('"')
        elif p_br.match(line):
            if i < max_i:
                if p_date.match(talk_data[i+1]):
                    continue
                else:
                    msg += "\n"
            else:
                print("error in br")
                
        else:
            print("\n   exception occurs in parse_talk_history() function  \n")
            print(f"line :{i}")
            print(line)
            
    # 最終行を保存
    talk_history_list.append([date, time, name, msg, flag])
    # リスト形式を一斉にデータフレームに変換するほうが早い
    talk_history = pd.DataFrame(talk_history_list, columns=["日付", "時刻", "発言者", "内容", "flag"])
    
    return title, save_date, talk_history


def main():
    # 扱いたい友人名を読み込む
    with open(f"./friend_names.txt", encoding="UTF-8") as f:
        friend_names = f.read().splitlines()
    
    for friend_name in friend_names:
        with open(f"./トーク/[LINE] {friend_name}とのトーク.txt", encoding="UTF-8") as f:
            talk_txt = f.readlines()
            
        # トーク履歴をクレンジング
        cleansed_talk_txt = cleanse_txt(talk_txt)
        # トーク履歴をparse
        title, save_date, parsed_talk_history = parse_talk_history(cleansed_talk_txt)
        # ワードクラウドを作成
        # create_wordcloud(talk_history, fr_name, i)
        # 語彙数を計測
        # my_voc, fr_voc, total_my_num, total_fr_num = vocabulary_check(talk_history, friend_name)
        
        print("------------------------------------------------")
        print(f"title: {title}")
        print(f"save date: {save_date}\n")
        
        print("\t相手の発言数:", parsed_talk_history.query(f"発言者 == '{friend_name}'").query("flag == 10")["flag"].count())
        print("\tあなたの発言数:", parsed_talk_history.query(f"発言者 == '{MY_NAME}'").query("flag == 10")["flag"].count())
        print("-------------------------------------------------")
        # flag
        # -1 : saved data
        # 10 : talk message
        # 11 : delete message 相手が取り消した場合
        # 12 : delete message 自分が取り消した場合
        # 20 : stamp
        # 21 : photo
        # 22 : video
        # 23 : address
        # 30 : call
        # 31 : missed call 不在着信
        # 32 : canceled call 通話をキャンセルしました
        # 33 : no answer call 通話に応答がありませんでした
        # 34 : invited call ☎ グループ音声通話に招待されました。
        # 50 : system message unsent
        # 60 : file
        # 70 : create and add album
        # 71 : changed the name of the album
        # 72 : deleted the album

if __name__ == "__main__":
    start = time.time()    
    talk_history = main()
    end = time.time()    
    print(end-start, '秒')
    