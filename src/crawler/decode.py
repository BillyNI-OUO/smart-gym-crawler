from src.crawler.place import place
import sys
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
		
		#地址 #503
		formatted_address = str(data[0][1][i][14][183][0][2][1][0][0])
		
		#cid_1, cid_2 #27
		ox = data[0][1][i][14][10].split(':')
		cid_1 = int(ox[0], 16)
		cid_2 = int(ox[1], 16)
		
		
		return place(place_id, cid_1, cid_2, name, lat, lng, formatted_address)
	except Exception as e:
		sys.stderr.write(str(e)+"\n")