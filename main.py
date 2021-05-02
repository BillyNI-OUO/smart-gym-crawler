#from src.crawler import *
import src
import src.crawler as crawler

#import src.sql as sql
from src.sql.connector import connector


con = connector()
"""
con.init_db()
"""
"""
l = crawler.grid.search_nearby2((22.0, 22.0002), (120.7440363, 120.7440563))
for i in l:
	print(i)
	con.insert_place(i)
	ll = crawler.query.reviews((i.cid_1, i.cid_2))
	con.insert_reviews(ll)
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
field = ['name', 'cid']
con.download_query(field = field, table = 'place', predicate = "WHERE cid = 16758945349437698000", filepath="")

"""


cids = []
with open("word_gym_cid.txt", "r") as fp:
	lines = fp.readlines()
	for line in lines:
		cids.append(int(line.split("\n")[0]))
links = []
with open("links.txt", "r") as fp2:
	lines = fp2.readlines()
	for line in lines:
		links.append(line)
results = []
result2 = []
field =['name']
for i, cid in enumerate(cids):
	result = con.query_place(field = field, predicate = f"WHERE cid = {cid}")
	if result:
		#results.append(str(result[0][0]))
		pass
	else:
		results.append(cid)
		result2.append(links[i])
print(f'Should query: {len(cids)}   Actual find: {len(cids)-len(results)}')
print(f'Correctness: {1-len(results)/len(cids)}')
print(f"Didn't query's cid: ")

for result in results:
	print(result)
with open("word_gym_url.txt", "with")as fp:
	for result in result2:
		fp.writelines(result)
