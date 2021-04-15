"""
The object used to storage the information of review
"""
class review :

	def __init__ (self, review_id, rating, time, text, author_name, author_id, cid):
		self.review_id = review_id
		self.rating = rating
		self.time = time
		self.text = text
		self.author_name = author_name
		self.author_id = author_id
		self.cid_1 = cid[0]
		self.cid_2 = cid[1]
	
	def __str__(self):
		return f'review_id : {self.review_id}\nrating : {self.rating}\ntime : {self.time}\ntext : {self.text[:10]}...\nauthor_name : {self.author_name}\nauthor_id : {self.author_id}'
