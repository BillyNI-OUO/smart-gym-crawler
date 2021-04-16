#from src.crawler import *
import src.crawler as crawler

#import src.sql as sql
from src.sql.connector import connector
con = connector()

con.init_db()

l = crawler.grid.search_nearby2((22.0, 22.0002), (120.7440363, 120.7440563))
for i in l:
	print(i)
	con.insert_place(i)
	ll = crawler.query.reviews((i.cid_1, i.cid_2))
	con.insert_reviews(ll)

