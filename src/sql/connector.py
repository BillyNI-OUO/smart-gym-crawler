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

			name = place.name.replace("'", "''")
			formatted_address = place.formatted_address.replace("'", "''")

			sql = f"\
				INSERT INTO place_info\
				(place_id, cid_1, cid, name, lat, lng, formatted_address, buisness)\
				VALUES\
				('{place.place_id}', {place.cid_1}, {place.cid_2}, '{name}', {place.lat}, {place.lng}, '{formatted_address}', {place.buisness})\
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
			text = review.text.replace("'", "''")
			author_name = review.author_name.replace("'", "''")

			sql = f"\
				INSERT INTO reviews\
				(cid_1, cid, text, rating, author_name, author_id, review_id, time)\
				VALUES\
				({review.cid_1}, {review.cid_2}, '{text}', {review.rating}, '{author_name}', '{review.author_id}', '{review.review_id}', '{review.time}')\
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
		insert multiple reviews (list) into table
		"""
		for review in reviews:
			self.insert_review(review)



	def query_place(self, field, predicate = None):
		"""
		Query place from place_info
		parameter:
		field		: target field
		predicate	: predicate
		"""		
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
		"""
		Query place from reviews
		parameter:
		field		: target field
		predicate	: predicate
		"""	
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
		"""
		Download the query result
		Parameter:
		table		: target table (place/review)
		field		: target field
		predicate	: predicate
		filepath	: output filepath
		"""
		schema = field
		if table == "place":
			resultSet = self.query_place(field = field, predicate = predicate)
		elif table == "review":
			resultSet = self.query_review(field = field, predicate = predicate)
		print(resultSet)
		filepath += str(round(datetime.datetime.now().timestamp())) + ".csv"
		with open(filepath, 'w', newline = '')as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(schema)
			writer.writerows(resultSet)
	
	def caculate_rating(self):
		"""
		Caculating the average rating, and reviews' amount.
		Update the result.
		"""
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
		self.update_rating(resultSet)
		
		
	def update_rating(self, resultSet):
		"""
		Update the table from the result of caculating_rating
		"""

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
		"""
		Set the place's buisness'tag
		Parameter:
		cid	: place's cid
		tag	: buisness tag (0/1/2)
		"""
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
		"""
		Execute SQL instruction
		"""
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
	
	def query(self, sql):
		"""
		Query SQL instruction
		"""
		c = self.con.cursor(dictionary=True, buffered=True)
		resultSet = None
		try:
			c.execute(sql)
			resultSet = c.fetchall()
		except Exception as e:
			sys.stderr.write(str(e)+"\n")
		finally:
			self.con.commit()
			c.close()
		return resultSet
	
	def get_lastId(self):
		"""
		Get the last classified review's id
		"""
		c = self.con.cursor()
		lastId = None
		try:
			c.execute(f"SELECT `id` FROM `reviews_aspect` ORDER BY `id` DESC LIMIT 1")
			lastId = c.fetchall()
		except Exception as e:
			sys.stderr.write(str(e)+"\n")
		finally:
			self.con.commit()
			c.close()
			return	lastId
	
	def text_classify(self, lastId):
		"""
		Classified the review
		Parameter:
		lastId : the last classified review's id
		"""
		c = self.con.cursor()
		try:
			c.execute(f"""
					INSERT INTO `reviews_aspect`
					(`id`, `cid`)
					SELECT `reviews`.`id`, `reviews`.`cid`
					FROM `reviews`
					WHERE
					`reviews`.`id` > {lastId}
					AND `reviews`.`text` IS NOT NULL
					AND `reviews`.`text` NOT LIKE "(??? Google ????????????)%"
					;
			""")
			self.con.commit()
			c.execute(f"""
					UPDATE `reviews_aspect`
					LEFT JOIN `reviews` ON `reviews_aspect`.`id` = `reviews`.`id`
					SET `reviews_aspect`.`is_cleanliness` = 1
					WHERE
					`reviews`.`id` > {lastId}
					AND 
					(
						`reviews`.`text` LIKE '%???%' OR 
						`reviews`.`text` LIKE '%???%' OR 
						`reviews`.`text` LIKE '%???%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%??????%' OR 
						`reviews`.`text` LIKE '%???%'
					)
					;
				""")
			self.con.commit()
			c.execute(f"""
						UPDATE `reviews_aspect`
						LEFT JOIN `reviews` ON `reviews_aspect`.`id` = `reviews`.`id`
						SET `reviews_aspect`.`is_value` = 1
						WHERE
						`reviews`.`id` > {lastId}
						AND 
						(
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%cp%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%???%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%'
						)
						;
				""")
			self.con.commit()
			c.execute(f"""
						UPDATE `reviews_aspect`
						LEFT JOIN `reviews` ON `reviews_aspect`.`id` = `reviews`.`id`
						SET `reviews_aspect`.`is_service` = 1
						WHERE
						`reviews`.`id` > {lastId}
						AND 
						(
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%????????????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%'
						)
						;
				""")
			self.con.commit()
			c.execute(f"""
						UPDATE `reviews_aspect`
						LEFT JOIN `reviews` ON `reviews_aspect`.`id` = `reviews`.`id`
						SET `reviews_aspect`.`is_atmosphere` = 1
						WHERE
						`reviews`.`id` > {lastId}
						AND 
						(
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%????????????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%????????????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%????????????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%????????????%' OR
							`reviews`.`text` LIKE '%????????????%' OR
							`reviews`.`text` LIKE '%????????????%' OR
							`reviews`.`text` LIKE '%???%' OR
							`reviews`.`text` LIKE '%????????????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%?????????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%?????????%' OR
							`reviews`.`text` LIKE '%????????????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%' OR
							`reviews`.`text` LIKE '%??????%'
						)
						;
				""")
			self.con.commit()
			c.execute(f"""
						UPDATE `reviews_aspect`
						LEFT JOIN `reviews` ON `reviews_aspect`.`id` = `reviews`.`id`
						SET `reviews_aspect`.`is_food` = 1
						WHERE
						`reviews`.`id` > {lastId}
						AND 
						(
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%????????????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%????????????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%???%' OR 
							`reviews`.`text` LIKE '%???%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%???%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%?????????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%??????%' OR 
							`reviews`.`text` LIKE '%???%' OR 
							`reviews`.`text` LIKE '%??????%'
						)
						;
				""")
			self.con.commit()

		except Exception as e:
			sys.stderr.write(str(e)+"\n")
		finally:
			c.close()

	def update_updateTime(self, updateTime, remark = None):
		"""
		Upadate the last update time
		Parameter:
		updateTime		: datetime.strftime("%Y-%m-%d %H:%M:%S")
		remark			: any comment
		"""
		c = self.con.cursor()
		if remark != None:
			sql = f"\
					INSERT INTO time\
					(lastupdate, remark)\
					VALUES\
					('{updateTime}', '{remark}')"
		else:
			sql = f"\
					INSERT INTO time\
					(lastupdate)\
					VALUES\
					('{updateTime}')"
		try:
			c.execute(sql)
		except Exception as e:
			sys.stderr.write(str(e)+"\n")
		finally:
			self.con.commit()
			c.close()
			
	def caculate_average(self):
		"""
		Update the average rating after inference
		"""
		c = self.con.cursor()
		sql = """REPLACE INTO `aspect_ratings` (
					`id`,
					`cid`,
					`atmosphere_rating`,
					`atmosphere_count`,
					`service_rating`,
					`service_count`,
					`food_rating`,
					`food_count`,
					`value_rating`,
					`value_count`,
					`cleanliness_rating`,
					`cleanliness_count`,
					`last_update`
					) 
					SELECT
						`place_info`.`id`,
						`reviews_aspect`.`cid`,
						AVG(`reviews_aspect`.`atmosphere_rating`),
						COUNT(`reviews_aspect`.`atmosphere_rating`),
						AVG(`reviews_aspect`.`service_rating`),
						COUNT(`reviews_aspect`.`service_rating`),
						AVG(`reviews_aspect`.`food_rating`),
						COUNT(`reviews_aspect`.`food_rating`),
						AVG(`reviews_aspect`.`value_rating`),
						COUNT(`reviews_aspect`.`value_rating`),
						AVG(`reviews_aspect`.`cleanliness_rating`),
						COUNT(`reviews_aspect`.`cleanliness_rating`),
						NOW()
					FROM `reviews_aspect`
					LEFT JOIN `place_info` ON `place_info`.`cid` = `reviews_aspect`.`cid`
					GROUP BY `reviews_aspect`.`cid`
					;
				"""
		try:
			c.execute(sql)
		except Exception as e:
			sys.stderr.write(str(e)+"\n")
		finally:
			self.con.commit()
			c.close()
	def update_user_rating_total(self):
		"""
		Update the user_rating_total 
		"""
		c = self.con.cursor()
		sql = """UPDATE place_info A
				INNER JOIN (SELECT cid, COUNT(cid) idcount, AVG(rating) avgrating FROM reviews GROUP BY cid) as B
				on B.cid = A.cid
				SET A.user_ratings_total = B.idcount, A.rating = B.avgrating"""
		try:
			c.execute(sql)
		except Exception as e:
			sys.stderr.out(str(e)+"\n")
		finally:
			self.con.commit()
			c.close()

	def get_feedback_missing_place(self):
		c = self.con.cursor()
		sql = "SELECT name, created_at FROM feedback_missing_place"
		resultSet = None
		try:
			c.execute(sql)
			resultSet = c.fetchall()
		except Exception as e:
			sys.stderr.out(str(e)+"\n")
		finally:
			self.con.commit()
			c.close()
			return resultSet
