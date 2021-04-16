"""
The object used to do the sql stuff safety
"""

import mysql.connector
import src.constants as constants
import sys
class connector:

	def __init__(self):
		"""
		create a mysql.connector base on constants.SQLCONFIG
		"""
		self.con = mysql.connector.connect(**constants.SQLCONFIG)
	
	def __del__(self):
		"""
		disconnect to the database
		"""
		self.con.close()


	def init_db(self):
		"""
		Iniitialize the database
		Create the table
		"""
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
			rating INTEGER NOT NULL,
			time TIMESTAMP NOT NULL,
			text TEXT NOT NULL,
			author_name TEXT,
			author_id VARCHAR(50),
			review_id VARCHAR(100) NOT NULL,
			PRIMARY KEY(review_id)
			)""")
		self.con.commit()
		c.close()

	def is_place_exists(self, place):
		"""
		return if the place is existed in table by cid
		"""
		c = self.con.cursor()
		sql = f"\
			SELECT cid_1, cid_2 FROM tplace_info WHERE (cid_1, cid_2) = ('{place.cid_1}', '{place.cid_2}')\
			"
		c.execute(sql)
		if c.fetchone() == None:
			c.close()
			return False
		return True
	
	def is_review_exists(self, review):
		"""
		return if the review is existed in table by cid
		"""
		c = self.con.cursor()
		sql = f"\
			SELECT review_id FROM treviews_info WHERE (review_id) = ('{review.review_id}')\
			"
		c.execute(sql)
		if c.fetchone() == None:
			c.close()
			return False
		return True


	def insert_place(self, place):
		"""
		insert place into table
		"""
		if not self.is_place_exists(place):
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
		"""
		insert multiple places (list) into table
		"""
		for place in places:
			self.insert_place(place)

	def insert_review(self, review):
		"""
		insert review into table
		"""
		if not self.is_review_exists(review):
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
		"""
		insert multiple review (list) into table
		"""
		for review in reviews:
			self.insert_review(review)





