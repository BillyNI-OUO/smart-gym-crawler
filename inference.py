#! /home/user/anaconda3/envs/billy/bin/python
# -*- coding: utf-8 -*-
from rating.model import RatingModel
import mysql.connector
from bert_serving.client import BertClient
import re
import numpy as np
import math
import time
from collections import defaultdict
import sys

BATCH_SIZE = 1000
count = 0
last_id = 38457636
if len(sys.argv) > 1:
    if sys.argv[1] != '-f':
        last_id = int(sys.argv[1])
print('start from:', last_id)

rm = RatingModel()

con = mysql.connector.connect(
    host= '140.114.53.129',        	# 主機名稱
	database= 'smart_restaurant',		# 資料庫名稱
	user= 'smartuser',            	# 帳號
	password= 'pp253&$@'  			# 密碼
)

bc = BertClient(check_length=False)

KEYWORDS = {
    'atmosphere': [
        '舒服', '感受', '燈光', '明亮', '舒適', '樓層', '室外', '戶外', '室內', '氣氛', '乾淨',
        '環境', '浪漫', '光影', '怡人', '風景', '景色', '蚊子', '涼爽', '美景', '景觀',
        '山水', '山清水秀', '夜幕', '奇觀', '春光', '春色', '秋色', '美景', '風月', '風光',
        '風物', '風景', '鳥語花香', '景', '景色', '景物', '景致', '湖光山色',
        '好受', '好過', '安適', '自在', '受用', '得勁', '爽快', '愜意', '滋潤', '舒心',
        '舒坦', '舒展', '舒暢', '適意', '氛圍', '真爽',
        '七嘴八舌', '人聲鼎沸', '人聲嘈雜', '吵', '沸沸揚揚', '喧嘩', '喧鬧',
        '喧擾', '喧騰', '喧囂', '聒噪', '亂哄哄', '煩囂', '鼎沸', '嘈雜', '嘈雜', '塵囂',
        '嘩然', '鬧哄哄',
        '秋高氣爽', '涼快', '清爽', '陰涼', '悶熱', '暑氣', '酷暑', '酷熱', '燥熱', '很熱', '浮躁'
    ],
    'food': [
        '好吃', '新鮮', '味道', '麻辣', '舌頭', '菜餚', '嚼勁', '肚子', '風味', '豐富', '餐點',
        '口感', '必吃', '菜色', '精緻', '樣式', '廉價', '食材', '食物', '油膩', '軟嫩', '熟食',
        '生食', '腥味', '可口', '好聞', '芳香',
        '入味', '五味俱全', '甘美', '合口', '回味', '多汁', '好吃', '好味', '利口', '美味',
        '美味可口', '香', '脆', '夠味', '清口', '清爽', '爽口', '爽脆', '甜爽', '酥',
        '酥脆', '順口', '新鮮', '對味', '胃口', '適口', '膽美', '鮮', '鬆脆'
    ],
    'value': [
        '價格', '合理', '實惠', 'cp', '超值', '豐富', '貴', '平價', '豐盛'
    ],
    'service': [
        '服務', '粗魯', '溝通', '訂位', '感受', '預約', '人員', '溫暖', '耐心', '馬上', '態度',
        '用餐品質', '帶位', '道歉', '招待', '差勁', '友善', '臭臉', '店員', '動線', '盡職', '耐煩',
        '耐性', '暴躁', '煩躁', '急躁', '冒失', '輕率', '勝任'
    ],
    'cleanliness': [
        '污', '髒', '蟲', '蟑螂', '小強', '乾淨', '打掃', '衛生', '異物', '怪味', '腥味', '酸臭',
        '發霉', '黴菌', '安全', '清潔', '潔淨', '整潔', '頭髮', '茶漬', '垢', '噁心'
    ]
}

ASPECTS = ['atmosphere', 'service', 'food', 'cleanliness', 'value']


def is_aspect(aspect, sentence):
    global KEYWORDS
    for keyword in KEYWORDS[aspect]:
        if keyword in sentence:
            return True
    return False

def split_review_text_iter(review_text):
    if review_text is None:
        return
    for line in review_text.splitlines():
        stripped_line = line.strip()
        if len(stripped_line) == 0:
            continue

        for sep_line in re.split('。|，|；|﹐|！|\!|,|\?|？|；|;|\t|:|：', stripped_line):
            sep_line = sep_line.strip()
            if len(sep_line) > 20 or len(sep_line) <= 2:
                continue
            yield sep_line

print('starting...')

while True:
    st = time.time()
    cur = con.cursor(dictionary=True, buffered=True)
    cur.execute(f'''
    SELECT
        A.`id`, B.`text`, A.`is_atmosphere`,
        A.`is_service`, A.`is_food`, A.`is_cleanliness`, A.`is_value`
    FROM `reviews_aspect` AS A
    LEFT JOIN `reviews` AS B ON A.`id` = B.`id`
    WHERE
        A.`id` > {last_id} AND
        (
            A.`is_atmosphere` = 1 OR
            A.`is_service` = 1 OR
            A.`is_food` = 1 OR
            A.`is_cleanliness` = 1 OR
            A.`is_value` = 1
        )
    LIMIT {BATCH_SIZE};
    ''')
    reviews = cur.fetchall()
    if reviews is None or len(reviews) == 0:
        print('finish')
        break
    last_id = reviews[-1]['id']
    cur.close()
    
    splitted_sen = []
    sid = 0
    for review in reviews:
        text = review['text']
        review['aspects'] = defaultdict(list)
        review_aspects = tuple(filter(lambda v: review[f'is_{v}'] == 1, ASPECTS))
        for sen in split_review_text_iter(text):
            s_aspects = tuple(filter(lambda v: is_aspect(v, sen), review_aspects))
            if not any(s_aspects):
                continue
            splitted_sen.append(sen)
            
            for a in s_aspects:
                review['aspects'][a].append(sid)
            
            sid += 1
    
    if len(splitted_sen) == 0:
        print('skip!')
        print('count:', count, '\t', 'last index:', last_id)
        count += BATCH_SIZE
        continue
    
    splitted_emb = bc.encode(splitted_sen)
    splitted_rating = rm.predict_classes_embeddings(splitted_emb)
    
    results = []
    for review in reviews:
        ra = review['aspects']
        ar = list(np.average([splitted_rating[v] for v in ra[a]]) for a in ASPECTS)
        
        results.append(tuple(None if math.isnan(r) else r for r in ar) + (review['id'],))
    
    
    cur = con.cursor()
    cur.executemany(f'''
    UPDATE `reviews_aspect`
    SET
        `atmosphere_rating` = %s,
        `service_rating` = %s,
        `food_rating` = %s,
        `cleanliness_rating` = %s,
        `value_rating` = %s
    WHERE
        `id` = %s
    ;''', results)
    con.commit()
    cur.close()
    
    count += BATCH_SIZE
    
    et = time.time()
    print('count:', count, '\t', 'last index:', last_id, '\t', 'time:', et - st)
    
    del splitted_emb
    del splitted_rating
    del splitted_sen
    del results
