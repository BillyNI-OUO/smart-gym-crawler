#from src.crawler import *
import src
import src.crawler as crawler

#import src.sql as sql
from src.sql.connector import connector


con = connector()

con.init_db()
"""
l = crawler.grid.search_nearby2(lat_range=(21.8, 24), lng_range=(120, 121))
for i in l:
	print(i)
	#con.insert_place(i)
	ll = crawler.query.reviews((i.cid_1, i.cid_2))
	#con.insert_reviews(ll)
"""
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
for cor in cor_list[5:]:
	place_list = crawler.query.nearby2(location = cor)
	for place in place_list:
		if place == None:
			break
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

con.caculate_rating()
