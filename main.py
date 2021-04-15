#from src.crawler import *
import src.crawler as crawler
l = crawler.query.nearby2()
for i in l:
	print(i)
