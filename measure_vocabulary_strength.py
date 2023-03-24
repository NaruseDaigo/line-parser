import re
import math
import MeCab

def vocabulary_check(talk_history, friend_name):
    mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    my_txt = "\n".join(talk_history.query(f"flag == 10 and 発言者 == '{MY_NAME}'")["内容"])
    ft_txt = "\n".join(talk_history.query(f"flag == 10 and 発言者 == '{friend_name}'")["内容"])
    my_mecabs = mecab.parse(my_txt).split('\n')[0:-2]
    fr_mecabs = mecab.parse(ft_txt).split('\n')[0:-2]
    
    my_words = []
    fr_words = []
    
    for line in my_mecabs:
        tmp = re.split('\t|,', line)
        my_words.append(tmp[0])
    for line in fr_mecabs:
        tmp = re.split('\t|,', line)
        fr_words.append(tmp[0])
    
    return len(set(my_words)), len(set(fr_words)), len(my_words), len(fr_words)

def print_vocabulary_info(voc, total_num):
    print(f"\t\t語彙数: {voc}")
    print(f"\t\t語彙pt: {voc / math.log10(total_num)} pt")


'''
以下はChatGPTによる実装例
この例では、tokenize 関数を用いてテキストを単語に分割し、
measure_vocabulary_strength 関数で語彙力を測定しています
。語彙力は、テキスト内の一意な単語数を全単語数で割ることで算出されます。
また、word_frequency は各単語の出現回数を示しています。
'''

import re
from collections import Counter

def tokenize(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return words

def measure_vocabulary_strength(text):
    words = tokenize(text)
    word_count = len(words)
    unique_words = len(set(words))
    word_frequency = Counter(words)

    vocabulary_strength = unique_words / word_count

    return vocabulary_strength, word_frequency

# 使用例
text = "The quick brown fox jumps over the lazy dog. The dog is very lazy."
vocabulary_strength, word_frequency = measure_vocabulary_strength(text)

print("Vocabulary strength:", vocabulary_strength)
print("Word frequency:", word_frequency)
