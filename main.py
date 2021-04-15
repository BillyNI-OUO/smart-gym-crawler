#from src.crawler import *
import src.crawler as crawler
#import src.sql as sql
from src.sql.connector import connector
con = connector()

con.init_db()

l = crawler.query.nearby2()
for i in l:
	print(i)
	con.insert_place(i)
	ll = crawler.query.reviews((i.cid_1, i.cid_2))
	for j in ll:
		con.insert_review(j)
		print(j)
