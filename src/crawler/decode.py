from src.crawler.place import place
import sys
def nearby2(data, i):
	try:
		name = str(data[0][1][i][14][11])
		lat = str(data[0][1][i][14][9][2])
		lng = str(data[0][1][i][14][9][3])
		place_id = str(data[0][1][i][14][78])
		formatted_address = str(data[0][1][i][14][2][0])
		#print(data[0][1][i][14][183][0][2][1][0])
		formatted_address = str(data[0][1][i][14][183][0][2][1][0][0])
		ox = data[0][1][i][14][10].split(':')
		cid_1 = int(ox[0], 16)
		cid_2 = int(ox[1], 16)
		item = place(place_id, cid_1, cid_2, name, lat, lng, formatted_address)
		return item
	except Exception as e:
		sys.stderr.write(e)