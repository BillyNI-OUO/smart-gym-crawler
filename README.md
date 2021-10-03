# README
## Introduction
![Packagist Stars (custom server)](https://img.shields.io/packagist/stars/BillyNI-OUO/smart-gym-crawler)![GitHub top language](https://img.shields.io/github/languages/top/BillyNI-OUO/smart-gym-crawler)![](https://img.shields.io/badge/python-3.8-informational)![](https://img.shields.io/badge/made%20by-billy-brightgreen)
## 目前架構
```
src 
 |-crawler
   |-query.py
   |-decode.py
   |-place.py
   |-review.py
   |-coordinate.py
   |-grid.py
 |-sql
   |-connector.py
 |-constants.py

coordinate
 |-台中.txt
 |-台南.txt
 |-台北.txt
 |-桃園.txt
 |-新竹.txt
 |-台灣.txt

model
 |-rating_model.h5

rating
 |-model.py

main.py
update.py
update.sh
text_classify.py
utils.py
inference.py
feedbackupdate.py


```
## 目前已完成的功能
### Crawler
1. *crawler.query* 搜尋經緯度附近的目標
    a. *nearby2()* 爬目標的基本資料(非API方法)
    - 以實作place_id, (cid_1, cid_2), name, formatted, 座標
    
    b. *reviews()* 根據爬到的(cid_1, cid_2)去爬評論(非API方法)
    - text, review_id, rating, author_name, author_id, time
    
    c. *check_biusness()* 根據給定的cid去搜尋是否還有在營業
    - 還可以用這個去做feedback 的 update(尚未實作)

2. *crawler.decode* Decode非API方法(1.a, 1.b, 1.c)爬到的資料建立*Place*和*Review*物件

3. *Place*和*Review*實作物件的建立

4. *grid* 給定範圍，網格式的去呼叫*crawler.query*的方法

5. *coordinate* 讀/coordinate/裡的座標檔案
    有分成兩種讀法，一種是讀特定城市檔案的座標，另一種是讀台灣所有城市中心的座標
 
### SQL
1. *connector* 實作SQL的connector，以正確且安全的方式去操作SQL，以及許許多多會操作到sql的函式
    a. *insert_place* 將place 正確的insert 到database中
    b. *insert_review* 將revirew 正確的insert 到database中
    c. *query_place(), query_review()* 搜尋place或review
    d. *caculate_rating(), update_rating()* 為了更新平均分數和總評論數(早期寫法極其沒有效率，還請後來的人參考*update_user_rating_total()* 的寫法改善)
    e. *get_lastId(), text_classify(), caculate_average()* 請參考資料更新SOP
    f. *update_updateTime()* 紀錄上次更新資料庫的時間，為了優化算法
### Constants
存放會用到一些基本的參數，例如sql sever的ip, username....
以及一些url的產生函式


---

## TODO
1. API方法的實作
2. 改善*caculating_rating(), update_rating()* 的寫法
3. 增加可以用cid來爬特定餐廳的方法(可以參考*check_buisness()* 基本上只差decode的部分)

---
## Usage
### Installation
```python
pip3 install requests
pip3 install mysql-connector-python
pip3 install numpy
#我忘了還有用到甚麼，有跳出來的可以再補上
```
### 使用方式
#### 更新資料庫
注意一定要先把bert 打開，參考資料庫更新SOP，不然會卡住
```python
bash update.sh
#會平行化的去執行update.py以及接著執行text_classify
```
#### 新增回報新餐廳
還卡在確定餐廳的階段，未完全完成，feedbackupdate.py裡已完成找尋cid的部分，剩餘階段可以從check_buisness()裡參考如何爬特定餐廳的資訊

#### 其餘使用方式
參考main.py或下方example 去寫出想要實現的功能
### Example
都放在main.py裡面，可以參考看看

搜尋台中某個座標格中的餐廳和評論並輸入到SQL Database中

```python
import src
import src.crawler as crawler
from src.sql.connector import connector

#讀取台中的所有座標格，沒一個座標格由一組經位度組成 ex:(lat_range=(21.9, 22), lng_range=(120.8, 121))
cor_list = crawler.coordinate.get_coordinate('./coordinates/台中.txt')
#建立SQL的connector
con = connector()
#Initialize Database
con.init_db()

#這裡取第2個座標格，得到一串Place的list，你也可以用迴圈包起來，循序的執行
l = crawler.grid.search_nearby2(cor_list[2][0], cor_list[2][1])

#對list中所有的place
for i in l:
    print(i)
    #看看有沒有成功insert到Database中
    if con.insert_place(i):
        #去爬出Place的評論，得到一串review的list
        ll = crawler.query.reviews((i.cid_1, i.cid))
        #insert review 到Database中
        con.insert_reviews(ll)


```
用全台灣所有城市中心座標去搜尋
```python
import src
import src.crawler as crawler
from src.sql.connector import connector

cor_list = crawler.coordinate.taiwan('./coordinates/台灣.txt')
for cor in cor_list:
	place_list = crawler.query.nearby2(location = cor)
	for place in place_list:
		if place == None:
			break
		if con.insert_place(place):
			review_list = crawler.query.reviews((place.cid_1, place.cid))
			con.insert_reviews(review_list)
```
更新評論並檢查還有沒有在營業
```python
import src
import src.crawler as crawler
from src.sql.connector import connector
#從SQL中找出所有系統中的餐廳
placeList = con.query_place(['cid_1', 'cid'])

for place in placeList:
	f#去檢查是否有營業
	tag = crawler.query.check_business(place[1])
	#更新SQL營業狀態
	con.update_buisness(place[1], tag)
    #去爬評論
	reviewlist = crawler.query.reviews((0,place[1]))
	for review in reviewList:
		#比較出還沒在系統中的評論(不加這個判斷不影響結果，但可以大幅加快更新速度，差1.6倍
		if datetime.strptime(review.time, "%Y-%m-%d %H:%M:%S") > lastupdate:
			con.insert_review(review)
```
還有很多小功能，詳細內容可以看程式碼註解


