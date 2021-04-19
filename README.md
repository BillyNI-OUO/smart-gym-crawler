# README
## Introduction
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
constnts.py

```
## 目前已完成的功能
### Crawler
1. *crawler.query* 搜尋經緯度附近的目標
    a. *nearby2()* 爬目標的基本資料(非API方法)
    - 以實作place_id, (cid_1, cid_2), name, formatted, 座標
    - 尚未實作rating, type, user_rating_total, price_level
    
    b. *reviews()* 根據爬到的(cid_1, cid_2)去爬評論(非API方法)
    - text, review_id, rating, author_name, author_id, time
2. *crawler.decode* Decode非API方法(1.a, 1.b)爬到的資料建立*Place*和*review*物件
3. *Place*和*Review*實作物件的建立
4. *grid* 給定範圍，網格式的去呼叫*crawler.query*的方法
5. *coordinate* 讀/coordinate/裡的座標檔案
### SQL
1. *connector* 實作SQL的connector，以正確且安全的方式去操作SQL
    a. *insert_place* 將place 正確的insert 到database中
    b. *insert_review* 將revire 正確的insert 到database中
    c. 還有一些基本的query的操作
### Constants
存放會用到一些基本的參數，例如sql sever的ip, username....
以及一些url的產生函式


---

## TODO
1. API方法的實作
2. 更多SQL的接頭(? 例如query裡面的資料? 建立新的table(?
3. decode更多的資料(非API方法中，還可以爬出很多資料^ ^
4. *coordinate_taiwan*(實作中)

---
## Usage
### Installation
```python
pip3 install requests
pip3 install mysql-connector-python
pip3 install numpy
```
### Example

搜尋台中某個座標格中的餐廳和評論並輸入到SQL Database中

```python
import src
import src.crawler as crawler
from src.sql.connector import connector

#讀取台中的所有座標格
cor_list = crawler.coordinate.get_coordinate('./coordinates/台中.txt')
#建立SQL的connector
con = connector()
#Initialize Database
con.init_db()

#這裡取第2個座標格，得到一串Place的list
l = crawler.grid.search_nearby2(cor_list[2][0], cor_list[2][1])

#對list中所有的place
for i in l:
    print(i)
    #看看有沒有成功insert到Database中
    if con.insert_place(i):
        #去爬出Place的評論，得到一串review的list
        ll = crawler.query.reviews((i.cid_1, i.cid_2))
        #insert review 到Database中
        con.insert_reviews(ll)


```
