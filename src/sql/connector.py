import mysql.connector
import src.constants as constants
import sys
class connector:

	def __init__(self):

		self.con = mysql.connector.connect(**constants.SQLCONFIG)
	
	def __del__(self):
		self.con.close()


	def init_db(self):
		c = self.con.cursor()
		c.execute("""CREATE TABLE IF NOT EXISTS tplace_info (
			pid SERIAL,
			place_id VARCHAR(100) NOT NULL,
			cid_1	VARCHAR(50) NOT NULL,
			cid_2	VARCHAR(50) NOT NULL,
			hide_id VARCHAR(100),
			name TEXT NOT NULL,
			lat VARCHAR(50),
			lng VARCHAR(50),
			formatted_address TEXT,
			user_ratings_total INTEGER,
			price_level TEXT,
			rating FLOAT,
			types TEXT,
			PRIMARY KEY(cid_1,cid_2)
			)""")

		self.con.commit()
		c.execute("""CREATE TABLE IF NOT EXISTS treviews_info(
			rid SERIAL,
			cid_1	VARCHAR(50) NOT NULL,
			cid_2	VARCHAR(50) NOT NULL,
			rating FLOAT NOT NULL,
			time TIMESTAMP NOT NULL,
			text TEXT NOT NULL,
			author_name TEXT,
			author_id VARCHAR(50),
			review_id VARCHAR(100) NOT NULL,
			PRIMARY KEY(review_id)
			)""")
		self.con.commit()
		c.close()



	def insert_place(self, place):
		c = self.con.cursor()
		sql = f"\
			INSERT INTO tplace_info\
			(place_id, cid_1, cid_2, name, lat, lng, formatted_address)\
			VALUES\
			('{place.place_id}', '{place.cid_1}', '{place.cid_2}', '{place.name}', {place.lat}, {place.lng}, '{place.formatted_address}')\
			"
		try:
			c.execute(sql)
			self.con.commit()
			c.close()
		except Exception as e:
			sys.stderr.write(str(e)+"\n")

	def insert_places(self, places):
		for place in places:
			self.insert_place(place)

	def insert_review(self, review):
		c = self.con.cursor()


		sql = f"\
			INSERT INTO treviews_info\
			(cid_1, cid_2, text, rating, author_name, author_id, review_id, time)\
			VALUES\
			('{review.cid_1}', '{review.cid_2}', '{review.text}', {review.rating}, '{review.author_name}', '{review.author_id}', '{review.review_id}', '{review.time}')\
			"
		try:
			c.execute(sql)
			self.con.commit()
			c.close()
		except Exception as e:
			sys.stderr.write(str(e)+"\n")


	def insert_reviews(self, reviews):
		for review in reviews:
			self.insert_reviews(review)





