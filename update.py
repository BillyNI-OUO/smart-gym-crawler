#! /home/user/anaconda3/envs/billy/bin/python
#from src.crawler import *
import src
import src.crawler as crawler
import sys
#import src.sql as sql
from src.sql.connector import connector
from datetime import datetime

con = connector()

con.init_db()



lastupdate = con.query(f"SELECT `lastupdate` FROM `time` ORDER BY `id` DESC LIMIT 1")[0]['lastupdate']
placeList = con.query_place(['cid_1', 'cid'])
#print(placeList)
if len(sys.argv) > 1:
	idex = int(sys.argv[1])
placesLength = len(placeList)


for place in placeList[int(placesLength/10*(idex-1)):int(placesLength/10*(idex))]:
	#print(place[1])
	tag = crawler.query.check_business(place[1])
	#print('tag:'+str(tag))
	con.update_buisness(place[1], tag)
	reviewList = crawler.query.reviews((0,place[1]))
	for review in reviewList:
		#con.insert_review(review)
		if datetime.strptime(review.time, "%Y-%m-%d %H:%M:%S") > lastupdate:
			con.insert_review(review)
			#print(review)

#con.update_updateTime(updateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S"), remark = "test")