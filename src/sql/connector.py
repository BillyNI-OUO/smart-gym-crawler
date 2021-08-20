"""
The object used to do the sql stuff safety
"""

import mysql.connector
import src.constants as constants
import sys
import csv
import datetime
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

		c.execute("""CREATE TABLE IF NOT EXISTS place_info (
			id SERIAL,
			place_id VARCHAR(27) NOT NULL,
			cid_1 BIGINT UNSIGNED NOT NULL,
			cid	BIGINT UNSIGNED NOT NULL,
			hide_id TEXT,
			name TEXT NOT NULL,
			lat DOUBLE,
			lng DOUBLE,
			formatted_address TEXT,
			user_ratings_total INTEGER,
			price_level TINYINT,
			rating FLOAT,
			types TEXT,
			buisness INT,
			PRIMARY KEY(id ,cid)
			)""")


		self.con.commit()

		c.execute("""CREATE TABLE IF NOT EXISTS reviews(
			id SERIAL,
			cid_1 BIGINT UNSIGNED NOT NULL,
			cid	BIGINT UNSIGNED NOT NULL,
			rating TINYINT NOT NULL,
			time TIMESTAMP NOT NULL,
			text TEXT NOT NULL,
			author_name TEXT,
			author_id TEXT,
			review_id TEXT NOT NULL,
			PRIMARY KEY(id, cid)
			)""")
		self.con.commit()
		c.close()

	def is_place_exists(self, place):
		"""
		return if the place is existed in table by cid
		"""
		c = self.con.cursor()
		sql = f"\
			SELECT cid FROM place_info WHERE cid = '{place.cid_2}'\
			"
		c.execute(sql)
		if c.fetchone() == None:
			c.close()
			return False
		c.close()
		return True
	
	def is_review_exists(self, review):
		"""
		return if the review is existed in table by cid
		"""
		exist = False
		c = self.con.cursor()
		sql = f"\
			SELECT review_id FROM reviews WHERE cid = {review.cid_2}\
			"
		try:
			c.execute(sql)
			resultSet = c.fetchall()
			for reviews in resultSet:
				if reviews[0] == review.review_id:
					exist = True
					break
			
		except Exception as e:
			sys.stderr.write(str(e)+"\n")
			exist = False
		finally:
			c.close()
			return exist

	def insert_place(self, place):
		"""
		insert place into table
		"""
		success = False
		if not self.is_place_exists(place):
			c = self.con.cursor()
			sql = f"\
				INSERT INTO place_info\
				(place_id, cid_1, cid, name, lat, lng, formatted_address, buisness)\
				VALUES\
				('{place.place_id}', {place.cid_1}, {place.cid_2}, '{place.name}', {place.lat}, {place.lng}, '{place.formatted_address}', {place.buisness})\
				"
			try:
				c.execute(sql)
				success = True
			except Exception as e:
				sys.stderr.write(str(e)+"\n")
				success = False
			finally:
				self.con.commit()
				c.close()
				return success
		return False
		
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
		success = False
		if not self.is_review_exists(review):
			c = self.con.cursor()


			sql = f"\
				INSERT INTO reviews\
				(cid_1, cid, text, rating, author_name, author_id, review_id, time)\
				VALUES\
				({review.cid_1}, {review.cid_2}, '{review.text}', {review.rating}, '{review.author_name}', '{review.author_id}', '{review.review_id}', '{review.time}')\
				"
			try:
				c.execute(sql)
				success = True
			except Exception as e:
				sys.stderr.write(str(e)+"\n")
				success = False
			finally:
				self.con.commit()
				c.close()
				return success
		return success

	def insert_reviews(self, reviews):
		"""
		insert multiple review (list) into table
		"""
		for review in reviews:
			self.insert_review(review)



	def query_place(self, field, predicate = None):		
		c = self.con.cursor()
		sql = f"SELECT {field if field == '*' else ', '.join(field)} from place_info {predicate if predicate != None else ''}"
		try:
			c.execute(sql)
			resultSet = c.fetchall()
		except Exception as e:
			sys.stderr.write(str(e)+"\n")
			resultSet = None
		finally:
			c.close()
		return resultSet			



	def query_review(self, field, predicate = None):
		c = self.con.cursor()
		sql = f"SELECT {field if field == '*' else ', '.join(field)} from reviews {predicate if predicate != None else ''}"
		try:
			c.execute(sql)
			resultSet = c.fetchall()
		except Exception as e:
			sys.stderr.write(str(e)+"\n")
			resultSet = None
		finally:
			c.close()
		return resultSet			


	def download_query(self, table, field, predicate, filepath):
		schema = field
		if table == "place":
			resultSet = self.query_place(field = field, predicate = predicate)
		elif table == "reviews":
			resultSet = self.query_review(field = field, predicate = predicate)
		print(resultSet)
		filepath += str(round(datetime.datetime.now().timestamp())) + ".csv"
		with open(filepath, 'w', newline = '')as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(schema)
			writer.writerows(resultSet)
	
	def caculate_rating(self):
		c = self.con.cursor()
		sql = f"SELECT cid, AVG(rating), COUNT(rating) FROM reviews WHERE cid > 13220927980898481423 GROUP by cid "
		try:
			c.execute(sql)
			resultSet = c.fetchall()
		except Exception as e:
			sys.stderr.write(str(e)+"\n")
			resultSet = None
		finally:
			c.close()
		print(resultSet[:10])
		self.update_rating(resultSet)
		
		
	def update_rating(self, resultSet):
		

		for result in resultSet:
			c = self.con.cursor()
			#print(result)
			sql = f"UPDATE place_info SET rating = {result[1]}, user_ratings_total = {result[2]} WHERE cid = {result[0]}"
			try:
				c.execute(sql)
			except Exception as e:
				sys.stderr.write(str(e)+"\n")
			finally:
				self.con.commit()
				c.close()
		"""
		with open("reviews.csv", "r")as csvfile:
			rows = csv.reader(csvfile)
			for row in rows:
				c = self.con.cursor()
				print(row)
				sql = f"UPDATE place_info SET rating = {row[1]}, user_ratings_total = {row[2]} WHERE cid = {row[0]}"
				try:
					c.execute(sql)
				except Exception as e:
					sys.stderr.write(str(e)+"\n")
					resultSet = None
				finally:
					self.con.commit()
					c.close()
		"""
	
	def update_buisness(self, cid, tag):
		c = self.con.cursor()

		sql = f'UPDATE place_info SET buisness = {tag} WHERE cid = {cid}'
		try:
			c.execute(sql)
		except Exception as e:
			sys.stderr.write(str(e)+"\n")
		finally:
			self.con.commit()
			c.close()
            



	def execute(self, sql):
		c = self.con.cursor(dictionary=True, buffered=True)
		resultSet = None
		try:
			c.execute(sql)
			#resultSet = c.fetchall()
		except Exception as e:
			sys.stderr.write(str(e)+"\n")
		finally:
			self.con.commit()
			c.close()
		return resultSet			