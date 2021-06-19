# -*- coding: utf-8 -*-
# This file is used to generate the constant and URL which using in crawler.



#The HTTP header for requests
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

KEYWORD = "restaurant"

SQLCONFIG={
	'host': '120.126.17.206',        			# 主機名稱
	'database': 'smart_restaurant_HongKong',	# 資料庫名稱
	'user': 'smartuser',            			# 帳號
	'password': 'pp253&$@'  					# 密碼
}


QUERY_SIZE = 300
GRID_WIDTH = 0.05
COORDINATE_FILEPATH = "./coordinates/"

#The URL-generator for src.crawler.query.nearby2
def nearby2_url(lat, lng, cnt, query_size = 500,  keyword = KEYWORD):
	'''
	The URL-generator for src.crawler.query.nearby2
	Parameter:
	lat, lng   : latitude, longitude
	cnt        : counter for query times, determined by src.crawler.query.nearby2()
	query_size : The size of query per time
	keyword    : The keyword you want to search
	-----------------------------------------------------------------------------------
	URL產生方法:
	可以參考附屬文件連結，沒事不要去看，很痛苦
	'''
	return f'https://www.google.com/search?tbm=map&authuser=0&hl=zh-TW&gl=tw&pb=!4m12!1m3!1d300.0!2d{lat}!3d{lng}!2m3!1f0!2f0!3f0!3m2!1i1573!2i1215!4f13.1!7i{query_size}!8i{query_size*cnt}!10b1!14b1!12m8!1m1!18b1!2m3!5m1!6e2!20e3!10b1!16b1!19m4!2m3!1i360!2i120!4i8!20m57!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240!7m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!9b0!22m2!1sKXcxX8DYH5eS0gS5y6OwDw!7e81!24m50!1m12!13m6!2b1!3b1!4b1!6i1!8b1!9b1!18m4!3b1!4b1!5b1!6b1!2b1!5m5!2b1!3b1!5b1!6b1!7b1!10m1!8e3!14m1!3b1!17b1!20m4!1e3!1e6!1e14!1e15!21e2!24b1!25b1!26b1!29b1!30m1!2b1!36b1!43b1!52b1!55b1!56m2!1b1!3b1!65m5!3m4!1m3!1m2!1i224!2i298!26m4!2m3!1i80!2i92!4i8!30m28!1m6!1m2!1i0!2i0!2m2!1i458!2i1215!1m6!1m2!1i1523!2i0!2m2!1i1573!2i1215!1m6!1m2!1i0!2i0!2m2!1i1573!2i20!1m6!1m2!1i0!2i1195!2m2!1i1573!2i1215!34m14!2b1!3b1!4b1!6b1!8m4!1b1!3b1!4b1!6b1!9b1!12b1!14b1!20b1!23b1!37m1!1e81!42b1!47m0!49m1!3b1!50m4!2e2!3m2!1b1!3b1!65m0&q={keyword}'


#The URL-generator for src.crawler.query.reviews
def reviews_url(cid, cnt, query_size = 199):
	'''
	The URL-generator for src.crawler.query.reviews
	Parameter:
	cid    	   : The cid of place
	cnt	       : counter of query time, determined by src.crawler.query.reviews()
	query_size : The size of query per time
	-----------------------------------------------------------------------------------
	URL產生方法:
	可以參考附屬文件連結，沒事不要去看，很痛苦
	'''


	return f'https://www.google.com/maps/preview/review/listentitiesreviews?authuser=0&hl=zh-TW&gl=tw&pb=!1m2!1y{cid[0]}!2y{cid[1]}!2m2!1i{query_size*cnt}!2i{query_size}'