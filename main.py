#from src.crawler import *
import src
import src.crawler as crawler

#import src.sql as sql
from src.sql.connector import connector
import time 


con = connector()

con.init_db()
run_start=time.time()
l = crawler.grid.search_nearby2((22.0, 25.0002), (120.7440363, 120.7440563))
for i in l:
	print(i)
	con.insert_place(i)
	ll = crawler.query.reviews((i.cid_1, i.cid_2))
	con.insert_reviews(ll)
run_end=time.time()
print("執行時間：%f 秒" %(run_end-run_start))

"""
cor_list = crawler.coordinate.get_coordinate('./coordinates/台中.txt')
con = connector()

con.init_db()

l = crawler.grid.search_nearby2(cor_list[2][0], cor_list[2][1])
for i in l:
	print(i)
	if con.insert_place(i):
		ll = crawler.query.reviews((i.cid_1, i.cid_2))
		con.insert_reviews(ll)
"""
"""
count = 1
cor_list = crawler.coordinate.taiwan('./coordinates/台灣.txt')
for cor in cor_list:
	place_list = crawler.query.nearby2(location = cor)
	for place in place_list:
		if con.insert_place(place):
			print(count)
			count += 1
			print(place)
			
			review_list = crawler.query.reviews((place.cid_1, place.cid_2))
			con.insert_reviews(review_list)
"""
"""
field = ['cid_1', 'cid']
con.download_query(field = field, table = 'place', predicate = "WHERE cid_1 = 1445430307838188779", filepath="")
"""