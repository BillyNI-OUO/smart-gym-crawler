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
					AND `reviews`.`text` NOT LIKE "(由 Google 提供翻譯)%"
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
						`reviews`.`text` LIKE '%污%' OR 
						`reviews`.`text` LIKE '%髒%' OR 
						`reviews`.`text` LIKE '%蟲%' OR 
						`reviews`.`text` LIKE '%蟑螂%' OR 
						`reviews`.`text` LIKE '%小強%' OR 
						`reviews`.`text` LIKE '%乾淨%' OR 
						`reviews`.`text` LIKE '%打掃%' OR 
						`reviews`.`text` LIKE '%衛生%' OR 
						`reviews`.`text` LIKE '%異物%' OR 
						`reviews`.`text` LIKE '%怪味%' OR 
						`reviews`.`text` LIKE '%腥味%' OR 
						`reviews`.`text` LIKE '%酸臭%' OR 
						`reviews`.`text` LIKE '%發霉%' OR 
						`reviews`.`text` LIKE '%黴菌%' OR 
						`reviews`.`text` LIKE '%安全%' OR 
						`reviews`.`text` LIKE '%清潔%' OR 
						`reviews`.`text` LIKE '%潔淨%' OR 
						`reviews`.`text` LIKE '%整潔%' OR 
						`reviews`.`text` LIKE '%頭髮%' OR 
						`reviews`.`text` LIKE '%茶漬%' OR 
						`reviews`.`text` LIKE '%垢%'
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
							`reviews`.`text` LIKE '%價格%' OR 
							`reviews`.`text` LIKE '%合理%' OR 
							`reviews`.`text` LIKE '%實惠%' OR 
							`reviews`.`text` LIKE '%cp%' OR 
							`reviews`.`text` LIKE '%超值%' OR 
							`reviews`.`text` LIKE '%豐富%' OR 
							`reviews`.`text` LIKE '%貴%' OR 
							`reviews`.`text` LIKE '%平價%' OR 
							`reviews`.`text` LIKE '%豐盛%'
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
							`reviews`.`text` LIKE '%服務%' OR
							`reviews`.`text` LIKE '%粗魯%' OR
							`reviews`.`text` LIKE '%溝通%' OR
							`reviews`.`text` LIKE '%訂位%' OR
							`reviews`.`text` LIKE '%感受%' OR
							`reviews`.`text` LIKE '%預約%' OR
							`reviews`.`text` LIKE '%人員%' OR
							`reviews`.`text` LIKE '%溫暖%' OR
							`reviews`.`text` LIKE '%耐心%' OR
							`reviews`.`text` LIKE '%馬上%' OR
							`reviews`.`text` LIKE '%態度%' OR
							`reviews`.`text` LIKE '%用餐品質%' OR
							`reviews`.`text` LIKE '%帶位%' OR
							`reviews`.`text` LIKE '%道歉%' OR
							`reviews`.`text` LIKE '%招待%' OR
							`reviews`.`text` LIKE '%差勁%' OR
							`reviews`.`text` LIKE '%友善%' OR
							`reviews`.`text` LIKE '%臭臉%' OR
							`reviews`.`text` LIKE '%店員%' OR
							`reviews`.`text` LIKE '%動線%' OR
							`reviews`.`text` LIKE '%盡職%' OR
							`reviews`.`text` LIKE '%耐煩%' OR
							`reviews`.`text` LIKE '%耐性%' OR
							`reviews`.`text` LIKE '%暴躁%' OR
							`reviews`.`text` LIKE '%煩躁%' OR
							`reviews`.`text` LIKE '%急躁%' OR
							`reviews`.`text` LIKE '%冒失%' OR
							`reviews`.`text` LIKE '%輕率%' OR
							`reviews`.`text` LIKE '%勝任%'
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
							`reviews`.`text` LIKE '%舒服%' OR
							`reviews`.`text` LIKE '%感受%' OR
							`reviews`.`text` LIKE '%燈光%' OR
							`reviews`.`text` LIKE '%明亮%' OR
							`reviews`.`text` LIKE '%舒適%' OR
							`reviews`.`text` LIKE '%樓層%' OR
							`reviews`.`text` LIKE '%室外%' OR
							`reviews`.`text` LIKE '%戶外%' OR
							`reviews`.`text` LIKE '%室內%' OR
							`reviews`.`text` LIKE '%氣氛%' OR
							`reviews`.`text` LIKE '%乾淨%' OR
							`reviews`.`text` LIKE '%環境%' OR
							`reviews`.`text` LIKE '%吵雜%' OR
							`reviews`.`text` LIKE '%浪漫%' OR
							`reviews`.`text` LIKE '%光影%' OR
							`reviews`.`text` LIKE '%怡人%' OR
							`reviews`.`text` LIKE '%風景%' OR
							`reviews`.`text` LIKE '%景色%' OR
							`reviews`.`text` LIKE '%蚊子%' OR
							`reviews`.`text` LIKE '%涼爽%' OR
							`reviews`.`text` LIKE '%美景%' OR
							`reviews`.`text` LIKE '%景觀%' OR
							`reviews`.`text` LIKE '%山水%' OR
							`reviews`.`text` LIKE '%山清水秀%' OR
							`reviews`.`text` LIKE '%夜幕%' OR
							`reviews`.`text` LIKE '%奇觀%' OR
							`reviews`.`text` LIKE '%春光%' OR
							`reviews`.`text` LIKE '%春色%' OR
							`reviews`.`text` LIKE '%秋色%' OR
							`reviews`.`text` LIKE '%美景%' OR
							`reviews`.`text` LIKE '%風月%' OR
							`reviews`.`text` LIKE '%風光%' OR
							`reviews`.`text` LIKE '%風物%' OR
							`reviews`.`text` LIKE '%風景%' OR
							`reviews`.`text` LIKE '%鳥語花香%' OR
							`reviews`.`text` LIKE '%景色%' OR
							`reviews`.`text` LIKE '%景物%' OR
							`reviews`.`text` LIKE '%景致%' OR
							`reviews`.`text` LIKE '%湖光山色%' OR
							`reviews`.`text` LIKE '%好受%' OR
							`reviews`.`text` LIKE '%好過%' OR
							`reviews`.`text` LIKE '%安適%' OR
							`reviews`.`text` LIKE '%自在%' OR
							`reviews`.`text` LIKE '%受用%' OR
							`reviews`.`text` LIKE '%得勁%' OR
							`reviews`.`text` LIKE '%爽快%' OR
							`reviews`.`text` LIKE '%愜意%' OR
							`reviews`.`text` LIKE '%滋潤%' OR
							`reviews`.`text` LIKE '%舒心%' OR
							`reviews`.`text` LIKE '%舒坦%' OR
							`reviews`.`text` LIKE '%舒展%' OR
							`reviews`.`text` LIKE '%舒暢%' OR
							`reviews`.`text` LIKE '%寫意%' OR
							`reviews`.`text` LIKE '%適意%' OR
							`reviews`.`text` LIKE '%氛圍%' OR
							`reviews`.`text` LIKE '%真爽%' OR
							`reviews`.`text` LIKE '%七嘴八舌%' OR
							`reviews`.`text` LIKE '%人聲鼎沸%' OR
							`reviews`.`text` LIKE '%人聲嘈雜%' OR
							`reviews`.`text` LIKE '%吵%' OR
							`reviews`.`text` LIKE '%沸沸揚揚%' OR
							`reviews`.`text` LIKE '%喧嘩%' OR
							`reviews`.`text` LIKE '%喧鬧%' OR
							`reviews`.`text` LIKE '%喧擾%' OR
							`reviews`.`text` LIKE '%喧騰%' OR
							`reviews`.`text` LIKE '%喧囂%' OR
							`reviews`.`text` LIKE '%聒噪%' OR
							`reviews`.`text` LIKE '%亂哄哄%' OR
							`reviews`.`text` LIKE '%煩囂%' OR
							`reviews`.`text` LIKE '%鼎沸%' OR
							`reviews`.`text` LIKE '%嘈吵%' OR
							`reviews`.`text` LIKE '%嘈雜%' OR
							`reviews`.`text` LIKE '%嘈雜%' OR
							`reviews`.`text` LIKE '%塵囂%' OR
							`reviews`.`text` LIKE '%嘩然%' OR
							`reviews`.`text` LIKE '%鬧哄哄%' OR
							`reviews`.`text` LIKE '%秋高氣爽%' OR
							`reviews`.`text` LIKE '%涼快%' OR
							`reviews`.`text` LIKE '%清爽%' OR
							`reviews`.`text` LIKE '%陰涼%' OR
							`reviews`.`text` LIKE '%悶熱%' OR
							`reviews`.`text` LIKE '%暑氣%' OR
							`reviews`.`text` LIKE '%酷暑%' OR
							`reviews`.`text` LIKE '%酷熱%' OR
							`reviews`.`text` LIKE '%燥熱%' OR
							`reviews`.`text` LIKE '%很熱%' OR
							`reviews`.`text` LIKE '%浮躁%'
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
							`reviews`.`text` LIKE '%好吃%' OR 
							`reviews`.`text` LIKE '%新鮮%' OR 
							`reviews`.`text` LIKE '%味道%' OR 
							`reviews`.`text` LIKE '%麻辣%' OR 
							`reviews`.`text` LIKE '%舌頭%' OR 
							`reviews`.`text` LIKE '%菜餚%' OR 
							`reviews`.`text` LIKE '%嚼勁%' OR 
							`reviews`.`text` LIKE '%肚子%' OR 
							`reviews`.`text` LIKE '%風味%' OR 
							`reviews`.`text` LIKE '%豐富%' OR 
							`reviews`.`text` LIKE '%餐點%' OR 
							`reviews`.`text` LIKE '%口感%' OR 
							`reviews`.`text` LIKE '%必吃%' OR 
							`reviews`.`text` LIKE '%菜色%' OR 
							`reviews`.`text` LIKE '%精緻%' OR 
							`reviews`.`text` LIKE '%樣式%' OR 
							`reviews`.`text` LIKE '%廉價%' OR 
							`reviews`.`text` LIKE '%食材%' OR 
							`reviews`.`text` LIKE '%食物%' OR 
							`reviews`.`text` LIKE '%油膩%' OR 
							`reviews`.`text` LIKE '%軟嫩%' OR 
							`reviews`.`text` LIKE '%熟食%' OR 
							`reviews`.`text` LIKE '%生食%' OR 
							`reviews`.`text` LIKE '%腥味%' OR 
							`reviews`.`text` LIKE '%可口%' OR 
							`reviews`.`text` LIKE '%好聞%' OR 
							`reviews`.`text` LIKE '%芳香撲鼻%' OR 
							`reviews`.`text` LIKE '%入味%' OR 
							`reviews`.`text` LIKE '%五味俱全%' OR 
							`reviews`.`text` LIKE '%甘美%' OR 
							`reviews`.`text` LIKE '%合口%' OR 
							`reviews`.`text` LIKE '%回味%' OR 
							`reviews`.`text` LIKE '%多汁%' OR 
							`reviews`.`text` LIKE '%好吃%' OR 
							`reviews`.`text` LIKE '%好味%' OR 
							`reviews`.`text` LIKE '%利口%' OR 
							`reviews`.`text` LIKE '%美味%' OR 
							`reviews`.`text` LIKE '%香%' OR 
							`reviews`.`text` LIKE '%脆%' OR 
							`reviews`.`text` LIKE '%夠味%' OR 
							`reviews`.`text` LIKE '%清口%' OR 
							`reviews`.`text` LIKE '%清爽%' OR 
							`reviews`.`text` LIKE '%爽口%' OR 
							`reviews`.`text` LIKE '%爽脆%' OR 
							`reviews`.`text` LIKE '%甜爽%' OR 
							`reviews`.`text` LIKE '%酥%' OR 
							`reviews`.`text` LIKE '%順口%' OR 
							`reviews`.`text` LIKE '%新鮮%' OR 
							`reviews`.`text` LIKE '%對味兒%' OR 
							`reviews`.`text` LIKE '%胃口%' OR 
							`reviews`.`text` LIKE '%適口%' OR 
							`reviews`.`text` LIKE '%膽美%' OR 
							`reviews`.`text` LIKE '%鮮%' OR 
							`reviews`.`text` LIKE '%鬆脆%'
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
				INNER JOIN (SELECT cid, COUNT(cid) idcount FROM reviews GROUP BY cid) as B
					on B.cid = A.cid
				SET A.user_ratings_total = B.idcount"""
		try:
			c.execute(sql)
		except Exception as e:
			sys.stderr.out(str(e)+"\n")
		finally:
			self.con.commit()
			c.close()