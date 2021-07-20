"""
The object used to storage the information of place
"""
class place:
	
	def __init__(self, place_id, cid_1, cid_2, name, lat, lng, formatted_address, buisness):
		self.place_id = place_id
		self.cid_1 = cid_1
		self.cid_2 = cid_2
		self.name = name
		self.lat = lat
		self.lng = lng
		self.formatted_address = formatted_address
		self.buisness = buisness

	def __str__(self):
		
		return f'place_id : {self.place_id}\ncid_1    : {self.cid_1}\ncid_2    : {self.cid_2}\nname     : {self.name}\nlat      : {self.lat}\nlng      : {self.lng}\nformatted_address : {self.formatted_address}\nbuisness : {self.buisness}'

