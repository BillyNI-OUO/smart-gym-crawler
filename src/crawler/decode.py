from src.crawler.place import place
from src.crawler.review import review
import sys
import datetime
def nearby2(data, i = 1):
	"""
	Deocde the data from query.nearby2()
	Parameter:
	data : the data query from src.crawler.query.nearby2()
	i    : the index of which the data need to be decoded, determined by src.crawler.query.nearby2()
	----------------------------------------------------------------------------------------------------
	Decode的方法可以參考sample.py裡，那是query下來的原始資料
	下面所有資料附註旁的是第一家資料在sample裡的行數
	如果需要在解析更多資料，可以去裡面看
	沒事不要去看，很痛苦
	"""
	try:
		#餐廳名稱 #28
		name = str(data[0][1][i][14][11])
		
		#經緯度 #26
		lat = str(data[0][1][i][14][9][2])
		lng = str(data[0][1][i][14][9][3])
		
		#place_id #226
		place_id = str(data[0][1][i][14][78])
		
		#地址 #19 or #503, 
		formatted_address = str(data[0][1][i][14][2][0])
		if formatted_address[0] not in list(range(0, 10)):
			formatted_address = str(data[0][1][i][14][183][0][2][1][0][0])
		
		#cid_1, cid_2 #27
		ox = data[0][1][i][14][10].split(':')
		cid_1 = int(ox[0], 16)
		cid_2 = int(ox[1], 16)
		
		
		return place(place_id, cid_1, cid_2, name, lat, lng, formatted_address, 0)
	except Exception as e:
		sys.stderr.write(str(e)+"\n")

def reviews(data, cid):
	"""
	Deocde the data from query.reviews()
	Parameter:
	data : the data query from src.crawler.query.reviews()
	"""
	try:
		if data[3] == None:
			return None	
		text = data[3]
		review_id = data[10]
		rating = data[4]
		author_name = data[0][1]
		author_id = data[6]
		time = datetime.datetime.fromtimestamp(data[27] // 1000).astimezone(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
		return review(review_id, rating, time, text, author_name, author_id, cid)
	except Exception as e:
		sys.stderr.write(str(e)+"\n")
		return None

def buisness(data):
	"""
	Decode the data from query.check_buisness() and return the tag
	0 : 正常營業
	1 : 永久停業
	2 : 暫停營業
	Parameter:
	data : the data from query.check_buisness()

	"""
	try:
		if data[6][203][1][4][0] == '永久停業':
			return 1
		if data[6][203][1][4][0] == '暫停營業':
			return 2
		return 0
	except Exception as e:
		sys.stderr.write(str(e)+"\n")
		return 0
	