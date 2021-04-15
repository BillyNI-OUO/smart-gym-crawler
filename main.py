#from src.crawler import *
import src.crawler as crawler
l = crawler.query.nearby2()
for i in l:
	print(i)
	ll = crawler.query.reviews((i.cid_1, i.cid_2))
	print("-------------------------")
	for i in ll:
		print(i)