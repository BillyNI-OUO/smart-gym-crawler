#! /home/user/anaconda3/envs/billy/bin/python
#from src.crawler import *
import src
import src.crawler as crawler
import os
#import src.sql as sql
from src.sql.connector import connector
from datetime import datetime



con = connector()


lastId = con.get_lastId()[0][0]
#lastId = 42933658
con.update_updateTime(updateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S"), remark = f"lastId: {lastId}")

con.text_classify(lastId)
del con
os.system(f'python3 inference.py {lastId}')
con = connector()
con.caculate_average()
con.update_user_rating_total()
del con
print("Finish Update!!")
