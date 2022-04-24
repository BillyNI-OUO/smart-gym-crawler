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
			print('text classifying')
			c.execute(f"""
					INSERT INTO `reviews_aspect`
					(`id`, `cid`)
					SELECT `reviews`.`id`, `reviews`.`cid`
					FROM `reviews`
					WHERE
					`reviews`.`id` > {lastId}
					AND `reviews`.`text` IS NOT NULL
					AND `reviews`.`text` NOT LIKE "%(translated by google)%"
					;
			""")
			self.con.commit()
			print('checking cleanliness')
			c.execute(f"""
					UPDATE `reviews_aspect`
					LEFT JOIN `reviews` ON `reviews_aspect`.`id` = `reviews`.`id`
					SET `reviews_aspect`.`is_cleanliness` = 1
					WHERE
					`reviews`.`id` > {lastId}
					AND 
					(
						`reviews`.`text` LIKE '%soil%' OR
						`reviews`.`text` LIKE '%unbecoming%' OR
						`reviews`.`text` LIKE '%scoping%' OR
						`reviews`.`text` LIKE '%hidden%' OR
						`reviews`.`text` LIKE '%lively%' OR
						`reviews`.`text` LIKE '%vicious%' OR
						`reviews`.`text` LIKE '%garlicky%' OR
						`reviews`.`text` LIKE '%scouring%' OR
						`reviews`.`text` LIKE '%cleanses%' OR
						`reviews`.`text` LIKE '%brush%' OR
						`reviews`.`text` LIKE '%smog%' OR
						`reviews`.`text` LIKE '%disgusting%' OR
						`reviews`.`text` LIKE '%hubby%' OR
						`reviews`.`text` LIKE '%nosey%' OR
						`reviews`.`text` LIKE '%humid%' OR
						`reviews`.`text` LIKE '%secure%' OR
						`reviews`.`text` LIKE '%lousy%' OR
						`reviews`.`text` LIKE '%soiled%' OR
						`reviews`.`text` LIKE '%sober%' OR
						`reviews`.`text` LIKE '%sludge%' OR
						`reviews`.`text` LIKE '%pesky%' OR
						`reviews`.`text` LIKE '%docility%' OR
						`reviews`.`text` LIKE '%untouched%' OR
						`reviews`.`text` LIKE '%stuffiness%' OR
						`reviews`.`text` LIKE '%neatly%' OR
						`reviews`.`text` LIKE '%big%' OR
						`reviews`.`text` LIKE '%tumble%' OR
						`reviews`.`text` LIKE '%righteousness%' OR
						`reviews`.`text` LIKE '%imprudent%' OR
						`reviews`.`text` LIKE '%contaminants%' OR
						`reviews`.`text` LIKE '%sweet%' OR
						`reviews`.`text` LIKE '%tubby%' OR
						`reviews`.`text` LIKE '%canny%' OR
						`reviews`.`text` LIKE '%uncleanly%' OR
						`reviews`.`text` LIKE '%waxed%' OR
						`reviews`.`text` LIKE '%carbs%' OR
						`reviews`.`text` LIKE '%limbered%' OR
						`reviews`.`text` LIKE '%contaminating%' OR
						`reviews`.`text` LIKE '%unwieldiest%' OR
						`reviews`.`text` LIKE '%grimier%' OR
						`reviews`.`text` LIKE '%scavenging%' OR
						`reviews`.`text` LIKE '%pestered%' OR
						`reviews`.`text` LIKE '%powdered%' OR
						`reviews`.`text` LIKE '%fuzzy%' OR
						`reviews`.`text` LIKE '%bored%' OR
						`reviews`.`text` LIKE '%dish%' OR
						`reviews`.`text` LIKE '%spooled%' OR
						`reviews`.`text` LIKE '%safekeeping%' OR
						`reviews`.`text` LIKE '%brutal%' OR
						`reviews`.`text` LIKE '%smeared%' OR
						`reviews`.`text` LIKE '%punch%' OR
						`reviews`.`text` LIKE '%tardy%' OR
						`reviews`.`text` LIKE '%gloominess%' OR
						`reviews`.`text` LIKE '%destructive%' OR
						`reviews`.`text` LIKE '%honest%' OR
						`reviews`.`text` LIKE '%cube%' OR
						`reviews`.`text` LIKE '%cleared%' OR
						`reviews`.`text` LIKE '%convincing%' OR
						`reviews`.`text` LIKE '%libel%' OR
						`reviews`.`text` LIKE '%puddled%' OR
						`reviews`.`text` LIKE '%whipple%' OR
						`reviews`.`text` LIKE '%chrome%' OR
						`reviews`.`text` LIKE '%immaculateness%' OR
						`reviews`.`text` LIKE '%weak%' OR
						`reviews`.`text` LIKE '%massey%' OR
						`reviews`.`text` LIKE '%vinegary%' OR
						`reviews`.`text` LIKE '%pebbly%' OR
						`reviews`.`text` LIKE '%wastewater%' OR
						`reviews`.`text` LIKE '%cesarean%' OR
						`reviews`.`text` LIKE '%drain%' OR
						`reviews`.`text` LIKE '%neat%' OR
						`reviews`.`text` LIKE '%messy%' OR
						`reviews`.`text` LIKE '%plums%' OR
						`reviews`.`text` LIKE '%chestnut%' OR
						`reviews`.`text` LIKE '%grey%' OR
						`reviews`.`text` LIKE '%boggled%' OR
						`reviews`.`text` LIKE '%scourging%' OR
						`reviews`.`text` LIKE '%negligent%' OR
						`reviews`.`text` LIKE '%honeyed%' OR
						`reviews`.`text` LIKE '%meek%' OR
						`reviews`.`text` LIKE '%confident%' OR
						`reviews`.`text` LIKE '%bale%' OR
						`reviews`.`text` LIKE '%sprawling%' OR
						`reviews`.`text` LIKE '%moisture%' OR
						`reviews`.`text` LIKE '%cage%' OR
						`reviews`.`text` LIKE '%wormy%' OR
						`reviews`.`text` LIKE '%moldered%' OR
						`reviews`.`text` LIKE '%rubbery%' OR
						`reviews`.`text` LIKE '%cleanse%' OR
						`reviews`.`text` LIKE '%contaminate%' OR
						`reviews`.`text` LIKE '%theft%' OR
						`reviews`.`text` LIKE '%catalyzing%' OR
						`reviews`.`text` LIKE '%bonding%' OR
						`reviews`.`text` LIKE '%complicated%' OR
						`reviews`.`text` LIKE '%pestering%' OR
						`reviews`.`text` LIKE '%housecleaned%' OR
						`reviews`.`text` LIKE '%ungrateful%' OR
						`reviews`.`text` LIKE '%woozy%' OR
						`reviews`.`text` LIKE '%coppery%' OR
						`reviews`.`text` LIKE '%fraction%' OR
						`reviews`.`text` LIKE '%houseclean%' OR
						`reviews`.`text` LIKE '%crabbier%' OR
						`reviews`.`text` LIKE '%tilt%' OR
						`reviews`.`text` LIKE '%stanchion%' OR
						`reviews`.`text` LIKE '%brassy%' OR
						`reviews`.`text` LIKE '%wasted%' OR
						`reviews`.`text` LIKE '%jaggedness%' OR
						`reviews`.`text` LIKE '%horsey%' OR
						`reviews`.`text` LIKE '%joke%' OR
						`reviews`.`text` LIKE '%cramped%' OR
						`reviews`.`text` LIKE '%cauterize%' OR
						`reviews`.`text` LIKE '%slanderous%' OR
						`reviews`.`text` LIKE '%unwarranted%' OR
						`reviews`.`text` LIKE '%iced%' OR
						`reviews`.`text` LIKE '%delicious%' OR
						`reviews`.`text` LIKE '%orderliness%' OR
						`reviews`.`text` LIKE '%cleans%' OR
						`reviews`.`text` LIKE '%uncontaminated%' OR
						`reviews`.`text` LIKE '%assimilate%' OR
						`reviews`.`text` LIKE '%pollinating%' OR
						`reviews`.`text` LIKE '%neighborliness%' OR
						`reviews`.`text` LIKE '%fouled%' OR
						`reviews`.`text` LIKE '%loveliness%' OR
						`reviews`.`text` LIKE '%sweet%' OR
						`reviews`.`text` LIKE '%lubber%' OR
						`reviews`.`text` LIKE '%bad%' OR
						`reviews`.`text` LIKE '%courtliness%' OR
						`reviews`.`text` LIKE '%joycean%' OR
						`reviews`.`text` LIKE '%oxidizing%' OR
						`reviews`.`text` LIKE '%gambling%' OR
						`reviews`.`text` LIKE '%scavenges%' OR
						`reviews`.`text` LIKE '%tainted%' OR
						`reviews`.`text` LIKE '%food%' OR
						`reviews`.`text` LIKE '%drag%' OR
						`reviews`.`text` LIKE '%foully%' OR
						`reviews`.`text` LIKE '%shuffle%' OR
						`reviews`.`text` LIKE '%luxuriousness%' OR
						`reviews`.`text` LIKE '%dumping%' OR
						`reviews`.`text` LIKE '%sandbagged%' OR
						`reviews`.`text` LIKE '%tidied%' OR
						`reviews`.`text` LIKE '%bothersome%' OR
						`reviews`.`text` LIKE '%sour%' OR
						`reviews`.`text` LIKE '%footman%' OR
						`reviews`.`text` LIKE '%adultery%' OR
						`reviews`.`text` LIKE '%foley%' OR
						`reviews`.`text` LIKE '%tailored%' OR
						`reviews`.`text` LIKE '%pebble%' OR
						`reviews`.`text` LIKE '%posy%' OR
						`reviews`.`text` LIKE '%cotton%' OR
						`reviews`.`text` LIKE '%carbonate%' OR
						`reviews`.`text` LIKE '%cool%' OR
						`reviews`.`text` LIKE '%insure%' OR
						`reviews`.`text` LIKE '%chamberlain%' OR
						`reviews`.`text` LIKE '%grimy%' OR
						`reviews`.`text` LIKE '%repellent%' OR
						`reviews`.`text` LIKE '%maddened%' OR
						`reviews`.`text` LIKE '%cutesy%' OR
						`reviews`.`text` LIKE '%vacuumed%' OR
						`reviews`.`text` LIKE '%scavenge%' OR
						`reviews`.`text` LIKE '%salted%' OR
						`reviews`.`text` LIKE '%uncleaner%' OR
						`reviews`.`text` LIKE '%baffling%' OR
						`reviews`.`text` LIKE '%blessedness%' OR
						`reviews`.`text` LIKE '%scrounge%' OR
						`reviews`.`text` LIKE '%blackened%' OR
						`reviews`.`text` LIKE '%cleanliness%' OR
						`reviews`.`text` LIKE '%strip%' OR
						`reviews`.`text` LIKE '%sterilizing%' OR
						`reviews`.`text` LIKE '%bizarre%' OR
						`reviews`.`text` LIKE '%simian%' OR
						`reviews`.`text` LIKE '%muted%' OR
						`reviews`.`text` LIKE '%untrustworthy%' OR
						`reviews`.`text` LIKE '%savaged%' OR
						`reviews`.`text` LIKE '%clearer%' OR
						`reviews`.`text` LIKE '%muddied%' OR
						`reviews`.`text` LIKE '%mcconnell%' OR
						`reviews`.`text` LIKE '%lumbered%' OR
						`reviews`.`text` LIKE '%plumbs%' OR
						`reviews`.`text` LIKE '%brave%' OR
						`reviews`.`text` LIKE '%worrisome%' OR
						`reviews`.`text` LIKE '%slime''s%' OR
						`reviews`.`text` LIKE '%dusty%' OR
						`reviews`.`text` LIKE '%tease%' OR
						`reviews`.`text` LIKE '%scraped%' OR
						`reviews`.`text` LIKE '%bribe%' OR
						`reviews`.`text` LIKE '%lick%' OR
						`reviews`.`text` LIKE '%acidifying%' OR
						`reviews`.`text` LIKE '%cemented%' OR
						`reviews`.`text` LIKE '%excess%' OR
						`reviews`.`text` LIKE '%stateliness%' OR
						`reviews`.`text` LIKE '%costliness%' OR
						`reviews`.`text` LIKE '%neatness%' OR
						`reviews`.`text` LIKE '%irresponsible%' OR
						`reviews`.`text` LIKE '%ungovernable%' OR
						`reviews`.`text` LIKE '%reedy%' OR
						`reviews`.`text` LIKE '%humble%' OR
						`reviews`.`text` LIKE '%nasty%' OR
						`reviews`.`text` LIKE '%incinerate%' OR
						`reviews`.`text` LIKE '%dummy%' OR
						`reviews`.`text` LIKE '%greenhorn%' OR
						`reviews`.`text` LIKE '%sordid%' OR
						`reviews`.`text` LIKE '%grunge%' OR
						`reviews`.`text` LIKE '%spirited%' OR
						`reviews`.`text` LIKE '%stretchy%' OR
						`reviews`.`text` LIKE '%bitter%' OR
						`reviews`.`text` LIKE '%damp%' OR
						`reviews`.`text` LIKE '%compacted%' OR
						`reviews`.`text` LIKE '%depleting%' OR
						`reviews`.`text` LIKE '%white%' OR
						`reviews`.`text` LIKE '%polite%' OR
						`reviews`.`text` LIKE '%whiter%' OR
						`reviews`.`text` LIKE '%peroxiding%' OR
						`reviews`.`text` LIKE '%singleton%' OR
						`reviews`.`text` LIKE '%ivory%' OR
						`reviews`.`text` LIKE '%scavenger%' OR
						`reviews`.`text` LIKE '%scrounged%' OR
						`reviews`.`text` LIKE '%bumbled%' OR
						`reviews`.`text` LIKE '%stringy%' OR
						`reviews`.`text` LIKE '%untruthful%' OR
						`reviews`.`text` LIKE '%gassy%' OR
						`reviews`.`text` LIKE '%nicely%' OR
						`reviews`.`text` LIKE '%plummet%' OR
						`reviews`.`text` LIKE '%soot%' OR
						`reviews`.`text` LIKE '%tidy%' OR
						`reviews`.`text` LIKE '%paint%' OR
						`reviews`.`text` LIKE '%cursed%' OR
						`reviews`.`text` LIKE '%muddled%' OR
						`reviews`.`text` LIKE '%homeliness%' OR
						`reviews`.`text` LIKE '%sordidness''s%' OR
						`reviews`.`text` LIKE '%unrealized%' OR
						`reviews`.`text` LIKE '%fighting%' OR
						`reviews`.`text` LIKE '%doughy%' OR
						`reviews`.`text` LIKE '%shale%' OR
						`reviews`.`text` LIKE '%weeded%' OR
						`reviews`.`text` LIKE '%shrink%' OR
						`reviews`.`text` LIKE '%horny%' OR
						`reviews`.`text` LIKE '%scavengers%' OR
						`reviews`.`text` LIKE '%fresh%' OR
						`reviews`.`text` LIKE '%unwashed%' OR
						`reviews`.`text` LIKE '%horrify%' OR
						`reviews`.`text` LIKE '%filthy%' OR
						`reviews`.`text` LIKE '%peat%' OR
						`reviews`.`text` LIKE '%gentles%' OR
						`reviews`.`text` LIKE '%ivory%' OR
						`reviews`.`text` LIKE '%materials%' OR
						`reviews`.`text` LIKE '%defective%' OR
						`reviews`.`text` LIKE '%chlorinating%' OR
						`reviews`.`text` LIKE '%plumb%' OR
						`reviews`.`text` LIKE '%clean%' OR
						`reviews`.`text` LIKE '%comfortable%' OR
						`reviews`.`text` LIKE '%questionable%' OR
						`reviews`.`text` LIKE '%grimness%' OR
						`reviews`.`text` LIKE '%cesarean%' OR
						`reviews`.`text` LIKE '%definite%' OR
						`reviews`.`text` LIKE '%buttock%' OR
						`reviews`.`text` LIKE '%patterned%' OR
						`reviews`.`text` LIKE '%dishonest%' OR
						`reviews`.`text` LIKE '%uncle%' OR
						`reviews`.`text` LIKE '%blanks%' OR
						`reviews`.`text` LIKE '%flirting%' OR
						`reviews`.`text` LIKE '%elegant%' OR
						`reviews`.`text` LIKE '%straightforward%' OR
						`reviews`.`text` LIKE '%respectable%' OR
						`reviews`.`text` LIKE '%sordidly%' OR
						`reviews`.`text` LIKE '%sleek%' OR
						`reviews`.`text` LIKE '%deposits%' OR
						`reviews`.`text` LIKE '%woodsy%' OR
						`reviews`.`text` LIKE '%pathetic%' OR
						`reviews`.`text` LIKE '%safe%' OR
						`reviews`.`text` LIKE '%housecleaning''s%' OR
						`reviews`.`text` LIKE '%unintelligent%' OR
						`reviews`.`text` LIKE '%loopy%' OR
						`reviews`.`text` LIKE '%chamberlain%' OR
						`reviews`.`text` LIKE '%stale%' OR
						`reviews`.`text` LIKE '%contaminant%' OR
						`reviews`.`text` LIKE '%selfless%' OR
						`reviews`.`text` LIKE '%sordidness%' OR
						`reviews`.`text` LIKE '%slime%' OR
						`reviews`.`text` LIKE '%hilly%' OR
						`reviews`.`text` LIKE '%footsore%' OR
						`reviews`.`text` LIKE '%ugly%' OR
						`reviews`.`text` LIKE '%scrounges%' OR
						`reviews`.`text` LIKE '%anderson%' OR
						`reviews`.`text` LIKE '%fraud%' OR
						`reviews`.`text` LIKE '%mean%' OR
						`reviews`.`text` LIKE '%swamped%' OR
						`reviews`.`text` LIKE '%corrosion%' OR
						`reviews`.`text` LIKE '%fight%' OR
						`reviews`.`text` LIKE '%shapeliness%' OR
						`reviews`.`text` LIKE '%tarbell%' OR
						`reviews`.`text` LIKE '%manipulation%' OR
						`reviews`.`text` LIKE '%striven%' OR
						`reviews`.`text` LIKE '%ungracious%' OR
						`reviews`.`text` LIKE '%blue%' OR
						`reviews`.`text` LIKE '%scenic%' OR
						`reviews`.`text` LIKE '%slippery%' OR
						`reviews`.`text` LIKE '%spying%' OR
						`reviews`.`text` LIKE '%sticky%' OR
						`reviews`.`text` LIKE '%jump%' OR
						`reviews`.`text` LIKE '%cotton%' OR
						`reviews`.`text` LIKE '%cooky%' OR
						`reviews`.`text` LIKE '%plodded%' OR
						`reviews`.`text` LIKE '%cute%' OR
						`reviews`.`text` LIKE '%strips%' OR
						`reviews`.`text` LIKE '%serene%' OR
						`reviews`.`text` LIKE '%discount%' OR
						`reviews`.`text` LIKE '%copying%' OR
						`reviews`.`text` LIKE '%chanter%' OR
						`reviews`.`text` LIKE '%stack%' OR
						`reviews`.`text` LIKE '%grimed%' OR
						`reviews`.`text` LIKE '%roadhouse%' OR
						`reviews`.`text` LIKE '%white%' OR
						`reviews`.`text` LIKE '%holman%' OR
						`reviews`.`text` LIKE '%cooking%' OR
						`reviews`.`text` LIKE '%balanced%' OR
						`reviews`.`text` LIKE '%cleansed%' OR
						`reviews`.`text` LIKE '%crisp%' OR
						`reviews`.`text` LIKE '%soils%' OR
						`reviews`.`text` LIKE '%glitter%' OR
						`reviews`.`text` LIKE '%miserable%' OR
						`reviews`.`text` LIKE '%greasy%' OR
						`reviews`.`text` LIKE '%wipe%' OR
						`reviews`.`text` LIKE '%spunky%' OR
						`reviews`.`text` LIKE '%stowing%' OR
						`reviews`.`text` LIKE '%volcanic%' OR
						`reviews`.`text` LIKE '%tap%' OR
						`reviews`.`text` LIKE '%watery%' OR
						`reviews`.`text` LIKE '%spitting%' OR
						`reviews`.`text` LIKE '%hobbs%' OR
						`reviews`.`text` LIKE '%scavenged%' OR
						`reviews`.`text` LIKE '%recycling%' OR
						`reviews`.`text` LIKE '%flinty%' OR
						`reviews`.`text` LIKE '%housecoat%' OR
						`reviews`.`text` LIKE '%muddy%' OR
						`reviews`.`text` LIKE '%horridly%' OR
						`reviews`.`text` LIKE '%cobs%' OR
						`reviews`.`text` LIKE '%risqu\u00e9%' OR
						`reviews`.`text` LIKE '%drip%' OR
						`reviews`.`text` LIKE '%petroleum%' OR
						`reviews`.`text` LIKE '%timer%' OR
						`reviews`.`text` LIKE '%clever%' OR
						`reviews`.`text` LIKE '%bedrock%' OR
						`reviews`.`text` LIKE '%lumpy%' OR
						`reviews`.`text` LIKE '%switching%' OR
						`reviews`.`text` LIKE '%warder%' OR
						`reviews`.`text` LIKE '%sister%' OR
						`reviews`.`text` LIKE '%purple%' OR
						`reviews`.`text` LIKE '%blubbered%' OR
						`reviews`.`text` LIKE '%sisterly%' OR
						`reviews`.`text` LIKE '%smoking%' OR
						`reviews`.`text` LIKE '%gritty%' OR
						`reviews`.`text` LIKE '%sandman%' OR
						`reviews`.`text` LIKE '%cheating%' OR
						`reviews`.`text` LIKE '%hateful%' OR
						`reviews`.`text` LIKE '%pigment%' OR
						`reviews`.`text` LIKE '%crumbling%' OR
						`reviews`.`text` LIKE '%fusty%' OR
						`reviews`.`text` LIKE '%falconer%' OR
						`reviews`.`text` LIKE '%dishonestly%' OR
						`reviews`.`text` LIKE '%temperament%' OR
						`reviews`.`text` LIKE '%bather%' OR
						`reviews`.`text` LIKE '%unsportsmanlike%' OR
						`reviews`.`text` LIKE '%mineral%' OR
						`reviews`.`text` LIKE '%cob%' OR
						`reviews`.`text` LIKE '%pink%' OR
						`reviews`.`text` LIKE '%bullock%' OR
						`reviews`.`text` LIKE '%precise%' OR
						`reviews`.`text` LIKE '%dandy%' OR
						`reviews`.`text` LIKE '%cleanness%' OR
						`reviews`.`text` LIKE '%grime''s%' OR
						`reviews`.`text` LIKE '%bamboozled%' OR
						`reviews`.`text` LIKE '%trading%' OR
						`reviews`.`text` LIKE '%misery%' OR
						`reviews`.`text` LIKE '%glide%' OR
						`reviews`.`text` LIKE '%raw%' OR
						`reviews`.`text` LIKE '%flashy%' OR
						`reviews`.`text` LIKE '%mousey%' OR
						`reviews`.`text` LIKE '%crusted%' OR
						`reviews`.`text` LIKE '%creel%' OR
						`reviews`.`text` LIKE '%herbicide%' OR
						`reviews`.`text` LIKE '%loyaler%' OR
						`reviews`.`text` LIKE '%kid%' OR
						`reviews`.`text` LIKE '%horrid%' OR
						`reviews`.`text` LIKE '%sanded%' OR
						`reviews`.`text` LIKE '%dingy%' OR
						`reviews`.`text` LIKE '%crisped%' OR
						`reviews`.`text` LIKE '%strawed%' OR
						`reviews`.`text` LIKE '%swanky%' OR
						`reviews`.`text` LIKE '%grime%' OR
						`reviews`.`text` LIKE '%disturbing%' OR
						`reviews`.`text` LIKE '%carboy%' OR
						`reviews`.`text` LIKE '%sealed%' OR
						`reviews`.`text` LIKE '%punch%' OR
						`reviews`.`text` LIKE '%wet%' OR
						`reviews`.`text` LIKE '%singleton%' OR
						`reviews`.`text` LIKE '%sister%' OR
						`reviews`.`text` LIKE '%grey%' OR
						`reviews`.`text` LIKE '%unfriendly%' OR
						`reviews`.`text` LIKE '%delicious%' OR
						`reviews`.`text` LIKE '%tooled%' OR
						`reviews`.`text` LIKE '%rummy%' OR
						`reviews`.`text` LIKE '%slash%' OR
						`reviews`.`text` LIKE '%wicked%' OR
						`reviews`.`text` LIKE '%refreshing%' OR
						`reviews`.`text` LIKE '%woodiness%' OR
						`reviews`.`text` LIKE '%soaked%' OR
						`reviews`.`text` LIKE '%bullock%' OR
						`reviews`.`text` LIKE '%bemoan%' OR
						`reviews`.`text` LIKE '%graveled%' OR
						`reviews`.`text` LIKE '%vaporizing%' OR
						`reviews`.`text` LIKE '%unclean%' OR
						`reviews`.`text` LIKE '%blank%' OR
						`reviews`.`text` LIKE '%barbs%' OR
						`reviews`.`text` LIKE '%sediment%' OR
						`reviews`.`text` LIKE '%orderly%' OR
						`reviews`.`text` LIKE '%straight%' OR
						`reviews`.`text` LIKE '%crawford%' OR
						`reviews`.`text` LIKE '%cement%' OR
						`reviews`.`text` LIKE '%tawdry%' OR
						`reviews`.`text` LIKE '%boozy%' OR
						`reviews`.`text` LIKE '%scatter%' OR
						`reviews`.`text` LIKE '%dirty%' OR
						`reviews`.`text` LIKE '%poker%' OR
						`reviews`.`text` LIKE '%chipped%' OR
						`reviews`.`text` LIKE '%plumb''s%' OR
						`reviews`.`text` LIKE '%alike%' OR
						`reviews`.`text` LIKE '%contaminates%' OR
						`reviews`.`text` LIKE '%lockean%' OR
						`reviews`.`text` LIKE '%resin%' OR
						`reviews`.`text` LIKE '%weedy%' OR
						`reviews`.`text` LIKE '%lowliness%' OR
						`reviews`.`text` LIKE '%twisted%' OR
						`reviews`.`text` LIKE '%appealing%' OR
						`reviews`.`text` LIKE '%healthy%' OR
						`reviews`.`text` LIKE '%metal%' OR
						`reviews`.`text` LIKE '%clear%' OR
						`reviews`.`text` LIKE '%jumpy%' OR
						`reviews`.`text` LIKE '%excreting%' OR
						`reviews`.`text` LIKE '%cleanser%' OR
						`reviews`.`text` LIKE '%uncleanest%' OR
						`reviews`.`text` LIKE '%housecleans%' OR
						`reviews`.`text` LIKE '%pureness%' OR
						`reviews`.`text` LIKE '%brother%' OR
						`reviews`.`text` LIKE '%incompetent%' OR
						`reviews`.`text` LIKE '%lock%' OR
						`reviews`.`text` LIKE '%foul%' OR
						`reviews`.`text` LIKE '%drinking%' OR
						`reviews`.`text` LIKE '%asphalted%' OR
						`reviews`.`text` LIKE '%fishy%' OR
						`reviews`.`text` LIKE '%ironed%' OR
						`reviews`.`text` LIKE '%uncleanlier%' OR
						`reviews`.`text` LIKE '%ancestor%' OR
						`reviews`.`text` LIKE '%pollution%' OR
						`reviews`.`text` LIKE '%battered%' OR
						`reviews`.`text` LIKE '%perfumed%' OR
						`reviews`.`text` LIKE '%cheap%' OR
						`reviews`.`text` LIKE '%haunted%' OR
						`reviews`.`text` LIKE '%healthiness%' OR
						`reviews`.`text` LIKE '%freshly%' OR
						`reviews`.`text` LIKE '%crumpled%' OR
						`reviews`.`text` LIKE '%deceitful%' OR
						`reviews`.`text` LIKE '%liveliness%' OR
						`reviews`.`text` LIKE '%basalt%' OR
						`reviews`.`text` LIKE '%sturdy%' OR
						`reviews`.`text` LIKE '%scavenger''s%' OR
						`reviews`.`text` LIKE '%friendliness%' OR
						`reviews`.`text` LIKE '%sandstone%' OR
						`reviews`.`text` LIKE '%oiled%' OR
						`reviews`.`text` LIKE '%shriveled%' OR
						`reviews`.`text` LIKE '%nerdier%' OR
						`reviews`.`text` LIKE '%shameful%' OR
						`reviews`.`text` LIKE '%stealing%' OR
						`reviews`.`text` LIKE '%colored%' OR
						`reviews`.`text` LIKE '%cleanly%' OR
						`reviews`.`text` LIKE '%lone%' OR
						`reviews`.`text` LIKE '%warped%' OR
						`reviews`.`text` LIKE '%muddles%' OR
						`reviews`.`text` LIKE '%unethical%' OR
						`reviews`.`text` LIKE '%cosy%' OR
						`reviews`.`text` LIKE '%crabby%' OR
						`reviews`.`text` LIKE '%sensible%' OR
						`reviews`.`text` LIKE '%tormented%' OR
						`reviews`.`text` LIKE '%defecate%' OR
						`reviews`.`text` LIKE '%thread%' OR
						`reviews`.`text` LIKE '%muffed%' OR
						`reviews`.`text` LIKE '%polluting%' OR
						`reviews`.`text` LIKE '%detoxification%' OR
						`reviews`.`text` LIKE '%fills%' OR
						`reviews`.`text` LIKE '%cousin%' OR
						`reviews`.`text` LIKE '%constant%' OR
						`reviews`.`text` LIKE '%plumbed%' OR
						`reviews`.`text` LIKE '%shiny%' OR
						`reviews`.`text` LIKE '%dusted%' OR
						`reviews`.`text` LIKE '%unexpected%' OR
						`reviews`.`text` LIKE '%uncleanliest%' OR
						`reviews`.`text` LIKE '%brotherly%' OR
						`reviews`.`text` LIKE '%seasoned%'
					)
					;
				""")
			self.con.commit()
			print('checking value')
			c.execute(f"""
						UPDATE `reviews_aspect`
						LEFT JOIN `reviews` ON `reviews_aspect`.`id` = `reviews`.`id`
						SET `reviews_aspect`.`is_value` = 1
						WHERE
						`reviews`.`id` > {lastId}
						AND 
						(
							`reviews`.`text` LIKE '%extremely%' OR
							`reviews`.`text` LIKE '%sleek%' OR
							`reviews`.`text` LIKE '%woodsy%' OR
							`reviews`.`text` LIKE '%suppliers%' OR
							`reviews`.`text` LIKE '%overpriced%' OR
							`reviews`.`text` LIKE '%measure%' OR
							`reviews`.`text` LIKE '%hurtle%' OR
							`reviews`.`text` LIKE '%pilfered%' OR
							`reviews`.`text` LIKE '%voltage%' OR
							`reviews`.`text` LIKE '%payments%' OR
							`reviews`.`text` LIKE '%manufactured%' OR
							`reviews`.`text` LIKE '%soiled%' OR
							`reviews`.`text` LIKE '%pressures%' OR
							`reviews`.`text` LIKE '%costly%' OR
							`reviews`.`text` LIKE '%brainy%' OR
							`reviews`.`text` LIKE '%predictions%' OR
							`reviews`.`text` LIKE '%value%' OR
							`reviews`.`text` LIKE '%compensate%' OR
							`reviews`.`text` LIKE '%authorized%' OR
							`reviews`.`text` LIKE '%velocity%' OR
							`reviews`.`text` LIKE '%elaborate%' OR
							`reviews`.`text` LIKE '%rents%' OR
							`reviews`.`text` LIKE '%bulky%' OR
							`reviews`.`text` LIKE '%pricing%' OR
							`reviews`.`text` LIKE '%unvoiced%' OR
							`reviews`.`text` LIKE '%undersized%' OR
							`reviews`.`text` LIKE '%costed%' OR
							`reviews`.`text` LIKE '%harmless%' OR
							`reviews`.`text` LIKE '%rate%' OR
							`reviews`.`text` LIKE '%tarmacked%' OR
							`reviews`.`text` LIKE '%market%' OR
							`reviews`.`text` LIKE '%bike%' OR
							`reviews`.`text` LIKE '%torque%' OR
							`reviews`.`text` LIKE '%fortune%' OR
							`reviews`.`text` LIKE '%prized%' OR
							`reviews`.`text` LIKE '%valuation%' OR
							`reviews`.`text` LIKE '%cute%' OR
							`reviews`.`text` LIKE '%costing%' OR
							`reviews`.`text` LIKE '%dimension%' OR
							`reviews`.`text` LIKE '%gap%' OR
							`reviews`.`text` LIKE '%blowsy%' OR
							`reviews`.`text` LIKE '%whiskey%' OR
							`reviews`.`text` LIKE '%horsepower%' OR
							`reviews`.`text` LIKE '%expenses%' OR
							`reviews`.`text` LIKE '%revenue%' OR
							`reviews`.`text` LIKE '%dangerous%' OR
							`reviews`.`text` LIKE '%neat%' OR
							`reviews`.`text` LIKE '%pious%' OR
							`reviews`.`text` LIKE '%pruned%' OR
							`reviews`.`text` LIKE '%proportion%' OR
							`reviews`.`text` LIKE '%greasy%' OR
							`reviews`.`text` LIKE '%marketed%' OR
							`reviews`.`text` LIKE '%terrifying%' OR
							`reviews`.`text` LIKE '%funding%' OR
							`reviews`.`text` LIKE '%wealth%' OR
							`reviews`.`text` LIKE '%fabrics%' OR
							`reviews`.`text` LIKE '%riches%' OR
							`reviews`.`text` LIKE '%subsidies%' OR
							`reviews`.`text` LIKE '%dollar%' OR
							`reviews`.`text` LIKE '%trajectory%' OR
							`reviews`.`text` LIKE '%pricey%' OR
							`reviews`.`text` LIKE '%mortgaged%' OR
							`reviews`.`text` LIKE '%quality%' OR
							`reviews`.`text` LIKE '%fun%' OR
							`reviews`.`text` LIKE '%overstocked%' OR
							`reviews`.`text` LIKE '%expensive%' OR
							`reviews`.`text` LIKE '%fined%' OR
							`reviews`.`text` LIKE '%pearson%' OR
							`reviews`.`text` LIKE '%fee%' OR
							`reviews`.`text` LIKE '%nominal%' OR
							`reviews`.`text` LIKE '%overprinted%' OR
							`reviews`.`text` LIKE '%timer%' OR
							`reviews`.`text` LIKE '%inexpensive%' OR
							`reviews`.`text` LIKE '%clever%' OR
							`reviews`.`text` LIKE '%radius%' OR
							`reviews`.`text` LIKE '%useless%' OR
							`reviews`.`text` LIKE '%overprice%' OR
							`reviews`.`text` LIKE '%cash%' OR
							`reviews`.`text` LIKE '%calculated%' OR
							`reviews`.`text` LIKE '%energetic%' OR
							`reviews`.`text` LIKE '%quantity%' OR
							`reviews`.`text` LIKE '%assessed%' OR
							`reviews`.`text` LIKE '%trusty%' OR
							`reviews`.`text` LIKE '%unbosomed%' OR
							`reviews`.`text` LIKE '%accursed%' OR
							`reviews`.`text` LIKE '%importance%' OR
							`reviews`.`text` LIKE '%measurement%' OR
							`reviews`.`text` LIKE '%dollars%' OR
							`reviews`.`text` LIKE '%priced%' OR
							`reviews`.`text` LIKE '%menacing%' OR
							`reviews`.`text` LIKE '%mandate%' OR
							`reviews`.`text` LIKE '%counterfeited%' OR
							`reviews`.`text` LIKE '%flyer%' OR
							`reviews`.`text` LIKE '%glide%' OR
							`reviews`.`text` LIKE '%booked%' OR
							`reviews`.`text` LIKE '%gamey%' OR
							`reviews`.`text` LIKE '%unique%' OR
							`reviews`.`text` LIKE '%flashy%' OR
							`reviews`.`text` LIKE '%price%' OR
							`reviews`.`text` LIKE '%bias%' OR
							`reviews`.`text` LIKE '%trained%' OR
							`reviews`.`text` LIKE '%wages%' OR
							`reviews`.`text` LIKE '%endurance%' OR
							`reviews`.`text` LIKE '%instructional%' OR
							`reviews`.`text` LIKE '%worthless%' OR
							`reviews`.`text` LIKE '%shipped%' OR
							`reviews`.`text` LIKE '%dicey%' OR
							`reviews`.`text` LIKE '%cone%' OR
							`reviews`.`text` LIKE '%artsy%' OR
							`reviews`.`text` LIKE '%skinny%' OR
							`reviews`.`text` LIKE '%prices%' OR
							`reviews`.`text` LIKE '%tariffs%' OR
							`reviews`.`text` LIKE '%clumsy%' OR
							`reviews`.`text` LIKE '%overprices%' OR
							`reviews`.`text` LIKE '%bizarre%' OR
							`reviews`.`text` LIKE '%price%' OR
							`reviews`.`text` LIKE '%gap%' OR
							`reviews`.`text` LIKE '%balance%' OR
							`reviews`.`text` LIKE '%cash%' OR
							`reviews`.`text` LIKE '%costs%' OR
							`reviews`.`text` LIKE '%installed%' OR
							`reviews`.`text` LIKE '%clearance%' OR
							`reviews`.`text` LIKE '%labelled%' OR
							`reviews`.`text` LIKE '%affordable%' OR
							`reviews`.`text` LIKE '%configured%' OR
							`reviews`.`text` LIKE '%intense%' OR
							`reviews`.`text` LIKE '%priceless%' OR
							`reviews`.`text` LIKE '%coin%' OR
							`reviews`.`text` LIKE '%excess%' OR
							`reviews`.`text` LIKE '%tactic%' OR
							`reviews`.`text` LIKE '%equipped%' OR
							`reviews`.`text` LIKE '%markets%' OR
							`reviews`.`text` LIKE '%money%' OR
							`reviews`.`text` LIKE '%asset%' OR
							`reviews`.`text` LIKE '%advertised%' OR
							`reviews`.`text` LIKE '%momentum%' OR
							`reviews`.`text` LIKE '%appealing%' OR
							`reviews`.`text` LIKE '%dewy%' OR
							`reviews`.`text` LIKE '%tuition%' OR
							`reviews`.`text` LIKE '%esteem%' OR
							`reviews`.`text` LIKE '%palmy%' OR
							`reviews`.`text` LIKE '%conditions%' OR
							`reviews`.`text` LIKE '%trendy%' OR
							`reviews`.`text` LIKE '%financing%' OR
							`reviews`.`text` LIKE '%powerful%' OR
							`reviews`.`text` LIKE '%invoiced%' OR
							`reviews`.`text` LIKE '%bullet%' OR
							`reviews`.`text` LIKE '%fishy%' OR
							`reviews`.`text` LIKE '%expense%' OR
							`reviews`.`text` LIKE '%impressive%' OR
							`reviews`.`text` LIKE '%lofty%' OR
							`reviews`.`text` LIKE '%values%' OR
							`reviews`.`text` LIKE '%overpaid%' OR
							`reviews`.`text` LIKE '%cheap%' OR
							`reviews`.`text` LIKE '%income%' OR
							`reviews`.`text` LIKE '%unrealized%' OR
							`reviews`.`text` LIKE '%profit%' OR
							`reviews`.`text` LIKE '%rates%' OR
							`reviews`.`text` LIKE '%subsidy%' OR
							`reviews`.`text` LIKE '%cost%' OR
							`reviews`.`text` LIKE '%heavier%' OR
							`reviews`.`text` LIKE '%filmy%' OR
							`reviews`.`text` LIKE '%boring%' OR
							`reviews`.`text` LIKE '%sturdy%' OR
							`reviews`.`text` LIKE '%tariff%' OR
							`reviews`.`text` LIKE '%sugarcoated%' OR
							`reviews`.`text` LIKE '%expenditure%' OR
							`reviews`.`text` LIKE '%yarn%' OR
							`reviews`.`text` LIKE '%amount%' OR
							`reviews`.`text` LIKE '%balls%' OR
							`reviews`.`text` LIKE '%daley%' OR
							`reviews`.`text` LIKE '%valued%' OR
							`reviews`.`text` LIKE '%dealers%' OR
							`reviews`.`text` LIKE '%salary%' OR
							`reviews`.`text` LIKE '%friction%' OR
							`reviews`.`text` LIKE '%leaky%' OR
							`reviews`.`text` LIKE '%overpricing%' OR
							`reviews`.`text` LIKE '%slam%' OR
							`reviews`.`text` LIKE '%buyer%' OR
							`reviews`.`text` LIKE '%tough%' OR
							`reviews`.`text` LIKE '%instruction%' OR
							`reviews`.`text` LIKE '%constant%' OR
							`reviews`.`text` LIKE '%compensation%' OR
							`reviews`.`text` LIKE '%comfortable%' OR
							`reviews`.`text` LIKE '%cheaper%' OR
							`reviews`.`text` LIKE '%weighty%' OR
							`reviews`.`text` LIKE '%shiny%' OR
							`reviews`.`text` LIKE '%scary%' OR
							`reviews`.`text` LIKE '%punishments%' OR
							`reviews`.`text` LIKE '%formulated%' OR
							`reviews`.`text` LIKE '%quantities%'
						)
						;
				""")
			self.con.commit()
			print('checking service')
			c.execute(f"""
						UPDATE `reviews_aspect`
						LEFT JOIN `reviews` ON `reviews_aspect`.`id` = `reviews`.`id`
						SET `reviews_aspect`.`is_service` = 1
						WHERE
						`reviews`.`id` > {lastId}
						AND 
						(
							`reviews`.`text` LIKE '%supplier%' OR
							`reviews`.`text` LIKE '%processors%' OR
							`reviews`.`text` LIKE '%advising%' OR
							`reviews`.`text` LIKE '%stools%' OR
							`reviews`.`text` LIKE '%cocktail%' OR
							`reviews`.`text` LIKE '%user%' OR
							`reviews`.`text` LIKE '%aid%' OR
							`reviews`.`text` LIKE '%venue%' OR
							`reviews`.`text` LIKE '%participant%' OR
							`reviews`.`text` LIKE '%combat%' OR
							`reviews`.`text` LIKE '%healers%' OR
							`reviews`.`text` LIKE '%management%' OR
							`reviews`.`text` LIKE '%goals%' OR
							`reviews`.`text` LIKE '%managerial%' OR
							`reviews`.`text` LIKE '%housekeepers%' OR
							`reviews`.`text` LIKE '%hostesses%' OR
							`reviews`.`text` LIKE '%journalism%' OR
							`reviews`.`text` LIKE '%serving%' OR
							`reviews`.`text` LIKE '%build%' OR
							`reviews`.`text` LIKE '%carry%' OR
							`reviews`.`text` LIKE '%managing%' OR
							`reviews`.`text` LIKE '%practicing%' OR
							`reviews`.`text` LIKE '%fisherman%' OR
							`reviews`.`text` LIKE '%secretary%' OR
							`reviews`.`text` LIKE '%stimulate%' OR
							`reviews`.`text` LIKE '%spectator%' OR
							`reviews`.`text` LIKE '%tailors%' OR
							`reviews`.`text` LIKE '%software%' OR
							`reviews`.`text` LIKE '%hostlers%' OR
							`reviews`.`text` LIKE '%coaches%' OR
							`reviews`.`text` LIKE '%trainer%' OR
							`reviews`.`text` LIKE '%participating%' OR
							`reviews`.`text` LIKE '%volunteer%' OR
							`reviews`.`text` LIKE '%serviceman%' OR
							`reviews`.`text` LIKE '%consultation%' OR
							`reviews`.`text` LIKE '%sponsor%' OR
							`reviews`.`text` LIKE '%nurse%' OR
							`reviews`.`text` LIKE '%programmer%' OR
							`reviews`.`text` LIKE '%jealous%' OR
							`reviews`.`text` LIKE '%feeder%' OR
							`reviews`.`text` LIKE '%interruption%' OR
							`reviews`.`text` LIKE '%provide%' OR
							`reviews`.`text` LIKE '%sacks%' OR
							`reviews`.`text` LIKE '%serves%' OR
							`reviews`.`text` LIKE '%interface%' OR
							`reviews`.`text` LIKE '%cast%' OR
							`reviews`.`text` LIKE '%waitresses%' OR
							`reviews`.`text` LIKE '%waitress%' OR
							`reviews`.`text` LIKE '%participants%' OR
							`reviews`.`text` LIKE '%coaching%' OR
							`reviews`.`text` LIKE '%appearing%' OR
							`reviews`.`text` LIKE '%butchers%' OR
							`reviews`.`text` LIKE '%entertain%' OR
							`reviews`.`text` LIKE '%assist%' OR
							`reviews`.`text` LIKE '%residing%' OR
							`reviews`.`text` LIKE '%casuals%' OR
							`reviews`.`text` LIKE '%waiters%' OR
							`reviews`.`text` LIKE '%organizer%' OR
							`reviews`.`text` LIKE '%porters%' OR
							`reviews`.`text` LIKE '%tablet%' OR
							`reviews`.`text` LIKE '%consultants%' OR
							`reviews`.`text` LIKE '%use%' OR
							`reviews`.`text` LIKE '%implementations%' OR
							`reviews`.`text` LIKE '%logistics%' OR
							`reviews`.`text` LIKE '%army%' OR
							`reviews`.`text` LIKE '%enlisted%' OR
							`reviews`.`text` LIKE '%mobile%' OR
							`reviews`.`text` LIKE '%servicemen%' OR
							`reviews`.`text` LIKE '%leadership%' OR
							`reviews`.`text` LIKE '%instructor%' OR
							`reviews`.`text` LIKE '%assurance%' OR
							`reviews`.`text` LIKE '%coach%' OR
							`reviews`.`text` LIKE '%bartender%' OR
							`reviews`.`text` LIKE '%feminine%' OR
							`reviews`.`text` LIKE '%working%' OR
							`reviews`.`text` LIKE '%claiming%' OR
							`reviews`.`text` LIKE '%exhibiting%' OR
							`reviews`.`text` LIKE '%illustrating%' OR
							`reviews`.`text` LIKE '%smartphone%' OR
							`reviews`.`text` LIKE '%position%' OR
							`reviews`.`text` LIKE '%commentator%' OR
							`reviews`.`text` LIKE '%marketing%' OR
							`reviews`.`text` LIKE '%browsers%' OR
							`reviews`.`text` LIKE '%finance%' OR
							`reviews`.`text` LIKE '%gardeners%' OR
							`reviews`.`text` LIKE '%guidance%' OR
							`reviews`.`text` LIKE '%feedback%' OR
							`reviews`.`text` LIKE '%napkins%' OR
							`reviews`.`text` LIKE '%absorb%' OR
							`reviews`.`text` LIKE '%distraction%' OR
							`reviews`.`text` LIKE '%goal%' OR
							`reviews`.`text` LIKE '%developer%' OR
							`reviews`.`text` LIKE '%kernel%' OR
							`reviews`.`text` LIKE '%serve%' OR
							`reviews`.`text` LIKE '%nutrition%' OR
							`reviews`.`text` LIKE '%counseling%' OR
							`reviews`.`text` LIKE '%hostess%' OR
							`reviews`.`text` LIKE '%training%' OR
							`reviews`.`text` LIKE '%tool%' OR
							`reviews`.`text` LIKE '%assistance%' OR
							`reviews`.`text` LIKE '%pass%' OR
							`reviews`.`text` LIKE '%fly%' OR
							`reviews`.`text` LIKE '%comprise%' OR
							`reviews`.`text` LIKE '%preach%' OR
							`reviews`.`text` LIKE '%ensign%' OR
							`reviews`.`text` LIKE '%services%' OR
							`reviews`.`text` LIKE '%keeper%' OR
							`reviews`.`text` LIKE '%suffering%' OR
							`reviews`.`text` LIKE '%auxiliary%' OR
							`reviews`.`text` LIKE '%hosts%' OR
							`reviews`.`text` LIKE '%organizers%' OR
							`reviews`.`text` LIKE '%dessert%' OR
							`reviews`.`text` LIKE '%drones%' OR
							`reviews`.`text` LIKE '%fridges%' OR
							`reviews`.`text` LIKE '%playing%' OR
							`reviews`.`text` LIKE '%patron%' OR
							`reviews`.`text` LIKE '%forward%' OR
							`reviews`.`text` LIKE '%fairy%' OR
							`reviews`.`text` LIKE '%clerk%' OR
							`reviews`.`text` LIKE '%support%' OR
							`reviews`.`text` LIKE '%trainers%' OR
							`reviews`.`text` LIKE '%brisk%' OR
							`reviews`.`text` LIKE '%enhancement%' OR
							`reviews`.`text` LIKE '%donors%' OR
							`reviews`.`text` LIKE '%simulator%' OR
							`reviews`.`text` LIKE '%functionality%' OR
							`reviews`.`text` LIKE '%promoter%' OR
							`reviews`.`text` LIKE '%switches%' OR
							`reviews`.`text` LIKE '%compiler%' OR
							`reviews`.`text` LIKE '%employ%' OR
							`reviews`.`text` LIKE '%technician%' OR
							`reviews`.`text` LIKE '%general%' OR
							`reviews`.`text` LIKE '%oracle%' OR
							`reviews`.`text` LIKE '%maid%' OR
							`reviews`.`text` LIKE '%instructional%' OR
							`reviews`.`text` LIKE '%covering%' OR
							`reviews`.`text` LIKE '%allowance%' OR
							`reviews`.`text` LIKE '%brunette%' OR
							`reviews`.`text` LIKE '%fulfill%' OR
							`reviews`.`text` LIKE '%bodyguard%' OR
							`reviews`.`text` LIKE '%waiter%' OR
							`reviews`.`text` LIKE '%illustrate%' OR
							`reviews`.`text` LIKE '%announcer%' OR
							`reviews`.`text` LIKE '%host%' OR
							`reviews`.`text` LIKE '%developers%' OR
							`reviews`.`text` LIKE '%displaying%' OR
							`reviews`.`text` LIKE '%assisting%' OR
							`reviews`.`text` LIKE '%goalkeeper%' OR
							`reviews`.`text` LIKE '%accounting%' OR
							`reviews`.`text` LIKE '%contestants%' OR
							`reviews`.`text` LIKE '%attending%' OR
							`reviews`.`text` LIKE '%depict%' OR
							`reviews`.`text` LIKE '%grooms%' OR
							`reviews`.`text` LIKE '%missions%' OR
							`reviews`.`text` LIKE '%duties%' OR
							`reviews`.`text` LIKE '%valets%' OR
							`reviews`.`text` LIKE '%paranoid%' OR
							`reviews`.`text` LIKE '%managers%' OR
							`reviews`.`text` LIKE '%outreach%' OR
							`reviews`.`text` LIKE '%goaltender%' OR
							`reviews`.`text` LIKE '%bakery%' OR
							`reviews`.`text` LIKE '%apps%' OR
							`reviews`.`text` LIKE '%operational%' OR
							`reviews`.`text` LIKE '%unit%' OR
							`reviews`.`text` LIKE '%undertake%' OR
							`reviews`.`text` LIKE '%browser%' OR
							`reviews`.`text` LIKE '%servers%' OR
							`reviews`.`text` LIKE '%shelter%' OR
							`reviews`.`text` LIKE '%intervention%' OR
							`reviews`.`text` LIKE '%finishing%' OR
							`reviews`.`text` LIKE '%historian%' OR
							`reviews`.`text` LIKE '%attendant%' OR
							`reviews`.`text` LIKE '%vocal%' OR
							`reviews`.`text` LIKE '%mobile%' OR
							`reviews`.`text` LIKE '%therapist%' OR
							`reviews`.`text` LIKE '%supervision%' OR
							`reviews`.`text` LIKE '%assists%' OR
							`reviews`.`text` LIKE '%confuse%' OR
							`reviews`.`text` LIKE '%teacher%' OR
							`reviews`.`text` LIKE '%receptionists%' OR
							`reviews`.`text` LIKE '%housekeeper%' OR
							`reviews`.`text` LIKE '%choreography%' OR
							`reviews`.`text` LIKE '%steals%' OR
							`reviews`.`text` LIKE '%commemorating%' OR
							`reviews`.`text` LIKE '%provision%' OR
							`reviews`.`text` LIKE '%server%' OR
							`reviews`.`text` LIKE '%pharmacy%' OR
							`reviews`.`text` LIKE '%secretary%' OR
							`reviews`.`text` LIKE '%headmaster%' OR
							`reviews`.`text` LIKE '%navy%' OR
							`reviews`.`text` LIKE '%wartime%' OR
							`reviews`.`text` LIKE '%service%' OR
							`reviews`.`text` LIKE '%format%' OR
							`reviews`.`text` LIKE '%portraying%' OR
							`reviews`.`text` LIKE '%successively%' OR
							`reviews`.`text` LIKE '%modeling%' OR
							`reviews`.`text` LIKE '%controllers%' OR
							`reviews`.`text` LIKE '%scoring%' OR
							`reviews`.`text` LIKE '%maids%' OR
							`reviews`.`text` LIKE '%contribution%' OR
							`reviews`.`text` LIKE '%mechanic%' OR
							`reviews`.`text` LIKE '%ethernet%' OR
							`reviews`.`text` LIKE '%linux%' OR
							`reviews`.`text` LIKE '%longtime%' OR
							`reviews`.`text` LIKE '%winger%' OR
							`reviews`.`text` LIKE '%desktop%' OR
							`reviews`.`text` LIKE '%infantry%' OR
							`reviews`.`text` LIKE '%specializing%' OR
							`reviews`.`text` LIKE '%witch%' OR
							`reviews`.`text` LIKE '%involvement%' OR
							`reviews`.`text` LIKE '%query%' OR
							`reviews`.`text` LIKE '%law%' OR
							`reviews`.`text` LIKE '%strategy%' OR
							`reviews`.`text` LIKE '%accompaniment%' OR
							`reviews`.`text` LIKE '%cache%' OR
							`reviews`.`text` LIKE '%cadet%' OR
							`reviews`.`text` LIKE '%served%' OR
							`reviews`.`text` LIKE '%flashlights%' OR
							`reviews`.`text` LIKE '%engineering%' OR
							`reviews`.`text` LIKE '%host''s%' OR
							`reviews`.`text` LIKE '%clones%' OR
							`reviews`.`text` LIKE '%arrogant%' OR
							`reviews`.`text` LIKE '%duty%' OR
							`reviews`.`text` LIKE '%hardware%' OR
							`reviews`.`text` LIKE '%diners%' OR
							`reviews`.`text` LIKE '%operate%' OR
							`reviews`.`text` LIKE '%referee%' OR
							`reviews`.`text` LIKE '%military%' OR
							`reviews`.`text` LIKE '%modems%' OR
							`reviews`.`text` LIKE '%oracle%' OR
							`reviews`.`text` LIKE '%manager%' OR
							`reviews`.`text` LIKE '%bartenders%' OR
							`reviews`.`text` LIKE '%receptionist%' OR
							`reviews`.`text` LIKE '%striker%'
						)
						;
				""")
			self.con.commit()
			print('checking atmosphere')
			c.execute(f"""
						UPDATE `reviews_aspect`
						LEFT JOIN `reviews` ON `reviews_aspect`.`id` = `reviews`.`id`
						SET `reviews_aspect`.`is_atmosphere` = 1
						WHERE
						`reviews`.`id` > {lastId}
						AND 
						(
							`reviews`.`text` LIKE '%cheerful%' OR
							`reviews`.`text` LIKE '%locations%' OR
							`reviews`.`text` LIKE '%ultraviolet%' OR
							`reviews`.`text` LIKE '%foregrounds%' OR
							`reviews`.`text` LIKE '%rotor%' OR
							`reviews`.`text` LIKE '%venue%' OR
							`reviews`.`text` LIKE '%radio%' OR
							`reviews`.`text` LIKE '%venues%' OR
							`reviews`.`text` LIKE '%mosaics%' OR
							`reviews`.`text` LIKE '%location%' OR
							`reviews`.`text` LIKE '%forest%' OR
							`reviews`.`text` LIKE '%magic%' OR
							`reviews`.`text` LIKE '%expression%' OR
							`reviews`.`text` LIKE '%marne%' OR
							`reviews`.`text` LIKE '%seascapes%' OR
							`reviews`.`text` LIKE '%gloom%' OR
							`reviews`.`text` LIKE '%nature%' OR
							`reviews`.`text` LIKE '%environments%' OR
							`reviews`.`text` LIKE '%techno%' OR
							`reviews`.`text` LIKE '%pedal%' OR
							`reviews`.`text` LIKE '%surround%' OR
							`reviews`.`text` LIKE '%weather%' OR
							`reviews`.`text` LIKE '%tumble%' OR
							`reviews`.`text` LIKE '%ghost%' OR
							`reviews`.`text` LIKE '%promotional%' OR
							`reviews`.`text` LIKE '%odor%' OR
							`reviews`.`text` LIKE '%ambiance''s%' OR
							`reviews`.`text` LIKE '%bliss%' OR
							`reviews`.`text` LIKE '%pacing%' OR
							`reviews`.`text` LIKE '%surrounds%' OR
							`reviews`.`text` LIKE '%wallpapering%' OR
							`reviews`.`text` LIKE '%screen%' OR
							`reviews`.`text` LIKE '%occult%' OR
							`reviews`.`text` LIKE '%scent%' OR
							`reviews`.`text` LIKE '%tenant%' OR
							`reviews`.`text` LIKE '%ambulatories%' OR
							`reviews`.`text` LIKE '%settings%' OR
							`reviews`.`text` LIKE '%aura%' OR
							`reviews`.`text` LIKE '%health%' OR
							`reviews`.`text` LIKE '%agitation%' OR
							`reviews`.`text` LIKE '%pipe%' OR
							`reviews`.`text` LIKE '%ventilation%' OR
							`reviews`.`text` LIKE '%stereo%' OR
							`reviews`.`text` LIKE '%sphere%' OR
							`reviews`.`text` LIKE '%radiance%' OR
							`reviews`.`text` LIKE '%atmosphere%' OR
							`reviews`.`text` LIKE '%airspace%' OR
							`reviews`.`text` LIKE '%soils%' OR
							`reviews`.`text` LIKE '%mixer%' OR
							`reviews`.`text` LIKE '%agricultural%' OR
							`reviews`.`text` LIKE '%forest%' OR
							`reviews`.`text` LIKE '%terrestrial%' OR
							`reviews`.`text` LIKE '%stance%' OR
							`reviews`.`text` LIKE '%ambiances%' OR
							`reviews`.`text` LIKE '%programming%' OR
							`reviews`.`text` LIKE '%landscape%' OR
							`reviews`.`text` LIKE '%console%' OR
							`reviews`.`text` LIKE '%fox%' OR
							`reviews`.`text` LIKE '%fusion%' OR
							`reviews`.`text` LIKE '%session%' OR
							`reviews`.`text` LIKE '%stimulation%' OR
							`reviews`.`text` LIKE '%lairs%' OR
							`reviews`.`text` LIKE '%vicinity%' OR
							`reviews`.`text` LIKE '%environment%' OR
							`reviews`.`text` LIKE '%visuals%' OR
							`reviews`.`text` LIKE '%acoustic%' OR
							`reviews`.`text` LIKE '%medley%' OR
							`reviews`.`text` LIKE '%lace%' OR
							`reviews`.`text` LIKE '%installation%' OR
							`reviews`.`text` LIKE '%intellectual%' OR
							`reviews`.`text` LIKE '%feedback%' OR
							`reviews`.`text` LIKE '%harmonic%' OR
							`reviews`.`text` LIKE '%fluctuations%' OR
							`reviews`.`text` LIKE '%nutrition%' OR
							`reviews`.`text` LIKE '%utilization%' OR
							`reviews`.`text` LIKE '%edifices%' OR
							`reviews`.`text` LIKE '%arctic%' OR
							`reviews`.`text` LIKE '%script%' OR
							`reviews`.`text` LIKE '%lifestyle%' OR
							`reviews`.`text` LIKE '%shipping%' OR
							`reviews`.`text` LIKE '%veranda%' OR
							`reviews`.`text` LIKE '%proportions%' OR
							`reviews`.`text` LIKE '%outsider%' OR
							`reviews`.`text` LIKE '%auras%' OR
							`reviews`.`text` LIKE '%halo%' OR
							`reviews`.`text` LIKE '%surroundings%' OR
							`reviews`.`text` LIKE '%scheduling%' OR
							`reviews`.`text` LIKE '%countryside%' OR
							`reviews`.`text` LIKE '%bisector%' OR
							`reviews`.`text` LIKE '%site%' OR
							`reviews`.`text` LIKE '%postscripts%' OR
							`reviews`.`text` LIKE '%mood%' OR
							`reviews`.`text` LIKE '%aerial%' OR
							`reviews`.`text` LIKE '%gazebo%' OR
							`reviews`.`text` LIKE '%temperament%' OR
							`reviews`.`text` LIKE '%kitchenette%' OR
							`reviews`.`text` LIKE '%pop%' OR
							`reviews`.`text` LIKE '%amulet%' OR
							`reviews`.`text` LIKE '%paste%' OR
							`reviews`.`text` LIKE '%exhume%' OR
							`reviews`.`text` LIKE '%landscaping%' OR
							`reviews`.`text` LIKE '%flavor%' OR
							`reviews`.`text` LIKE '%seraglios%' OR
							`reviews`.`text` LIKE '%morale%' OR
							`reviews`.`text` LIKE '%ecosystems%' OR
							`reviews`.`text` LIKE '%views%' OR
							`reviews`.`text` LIKE '%airline%' OR
							`reviews`.`text` LIKE '%casting%' OR
							`reviews`.`text` LIKE '%graphic%' OR
							`reviews`.`text` LIKE '%glamour%' OR
							`reviews`.`text` LIKE '%benefices%' OR
							`reviews`.`text` LIKE '%terrain%' OR
							`reviews`.`text` LIKE '%dioramas%' OR
							`reviews`.`text` LIKE '%outstations%' OR
							`reviews`.`text` LIKE '%organism%' OR
							`reviews`.`text` LIKE '%scented%' OR
							`reviews`.`text` LIKE '%supernatural%' OR
							`reviews`.`text` LIKE '%infrastructure%' OR
							`reviews`.`text` LIKE '%flight%' OR
							`reviews`.`text` LIKE '%emission%' OR
							`reviews`.`text` LIKE '%drum%' OR
							`reviews`.`text` LIKE '%posture%' OR
							`reviews`.`text` LIKE '%sentiment%' OR
							`reviews`.`text` LIKE '%demeanor%' OR
							`reviews`.`text` LIKE '%behavioral%' OR
							`reviews`.`text` LIKE '%effects%' OR
							`reviews`.`text` LIKE '%spice%' OR
							`reviews`.`text` LIKE '%illusion%' OR
							`reviews`.`text` LIKE '%environs''s%' OR
							`reviews`.`text` LIKE '%mystic%' OR
							`reviews`.`text` LIKE '%stench%' OR
							`reviews`.`text` LIKE '%tone%' OR
							`reviews`.`text` LIKE '%ceramic%' OR
							`reviews`.`text` LIKE '%accelerator%' OR
							`reviews`.`text` LIKE '%wallpapers%' OR
							`reviews`.`text` LIKE '%rhythm%' OR
							`reviews`.`text` LIKE '%infrared%' OR
							`reviews`.`text` LIKE '%fox%' OR
							`reviews`.`text` LIKE '%aroma%' OR
							`reviews`.`text` LIKE '%aural%' OR
							`reviews`.`text` LIKE '%facility%' OR
							`reviews`.`text` LIKE '%operational%' OR
							`reviews`.`text` LIKE '%footage%' OR
							`reviews`.`text` LIKE '%eyed%' OR
							`reviews`.`text` LIKE '%spaciousness%' OR
							`reviews`.`text` LIKE '%pictorials%' OR
							`reviews`.`text` LIKE '%depiction%' OR
							`reviews`.`text` LIKE '%ambiance%' OR
							`reviews`.`text` LIKE '%ambience''s%' OR
							`reviews`.`text` LIKE '%exhumes%' OR
							`reviews`.`text` LIKE '%airs%' OR
							`reviews`.`text` LIKE '%scenery%' OR
							`reviews`.`text` LIKE '%tactic%' OR
							`reviews`.`text` LIKE '%mix%' OR
							`reviews`.`text` LIKE '%sea%' OR
							`reviews`.`text` LIKE '%temper%' OR
							`reviews`.`text` LIKE '%lowlands%' OR
							`reviews`.`text` LIKE '%waterfronts%' OR
							`reviews`.`text` LIKE '%spray%' OR
							`reviews`.`text` LIKE '%strings%' OR
							`reviews`.`text` LIKE '%sample%' OR
							`reviews`.`text` LIKE '%blur%' OR
							`reviews`.`text` LIKE '%resonance%' OR
							`reviews`.`text` LIKE '%orb%' OR
							`reviews`.`text` LIKE '%airship%' OR
							`reviews`.`text` LIKE '%greeting%' OR
							`reviews`.`text` LIKE '%armories%' OR
							`reviews`.`text` LIKE '%arctic%' OR
							`reviews`.`text` LIKE '%sunlight%' OR
							`reviews`.`text` LIKE '%culture%' OR
							`reviews`.`text` LIKE '%stroll%' OR
							`reviews`.`text` LIKE '%spirit%' OR
							`reviews`.`text` LIKE '%pupil%' OR
							`reviews`.`text` LIKE '%ambiences%' OR
							`reviews`.`text` LIKE '%seashores%' OR
							`reviews`.`text` LIKE '%dangers%' OR
							`reviews`.`text` LIKE '%location''s%' OR
							`reviews`.`text` LIKE '%diversity%' OR
							`reviews`.`text` LIKE '%environs%' OR
							`reviews`.`text` LIKE '%lipstick%' OR
							`reviews`.`text` LIKE '%air%' OR
							`reviews`.`text` LIKE '%signal%' OR
							`reviews`.`text` LIKE '%kite%' OR
							`reviews`.`text` LIKE '%curiosities%' OR
							`reviews`.`text` LIKE '%loops%' OR
							`reviews`.`text` LIKE '%ambience%' OR
							`reviews`.`text` LIKE '%condor%' OR
							`reviews`.`text` LIKE '%racecourse%' OR
							`reviews`.`text` LIKE '%racing%' OR
							`reviews`.`text` LIKE '%salty%' OR
							`reviews`.`text` LIKE '%paranormal%' OR
							`reviews`.`text` LIKE '%smoky%' OR
							`reviews`.`text` LIKE '%fresh%' OR
							`reviews`.`text` LIKE '%apogees%' OR
							`reviews`.`text` LIKE '%somber%' OR
							`reviews`.`text` LIKE '%locality%' OR
							`reviews`.`text` LIKE '%recreations%' OR
							`reviews`.`text` LIKE '%ambient%' OR
							`reviews`.`text` LIKE '%talents%' OR
							`reviews`.`text` LIKE '%innovation%' OR
							`reviews`.`text` LIKE '%fragrance%' OR
							`reviews`.`text` LIKE '%amplifier%' OR
							`reviews`.`text` LIKE '%moodiness%' OR
							`reviews`.`text` LIKE '%porn%' OR
							`reviews`.`text` LIKE '%attitude%' OR
							`reviews`.`text` LIKE '%ink%' OR
							`reviews`.`text` LIKE '%sweetness%' OR
							`reviews`.`text` LIKE '%lushness%' OR
							`reviews`.`text` LIKE '%disrepair%' OR
							`reviews`.`text` LIKE '%vinyl%' OR
							`reviews`.`text` LIKE '%seraglio%' OR
							`reviews`.`text` LIKE '%sirius%'
						)
						;
				""")
			self.con.commit()
			print('checking food')
			c.execute(f"""
						UPDATE `reviews_aspect`
						LEFT JOIN `reviews` ON `reviews_aspect`.`id` = `reviews`.`id`
						SET `reviews_aspect`.`is_food` = 1
						WHERE
						`reviews`.`id` > {lastId}
						AND 
						(
							`reviews`.`text` LIKE '%earwig%' OR
							`reviews`.`text` LIKE '%cuisines%' OR
							`reviews`.`text` LIKE '%fruitless%' OR
							`reviews`.`text` LIKE '%drive%' OR
							`reviews`.`text` LIKE '%substrate%' OR
							`reviews`.`text` LIKE '%concentrate%' OR
							`reviews`.`text` LIKE '%bean%' OR
							`reviews`.`text` LIKE '%vine%' OR
							`reviews`.`text` LIKE '%braid%' OR
							`reviews`.`text` LIKE '%fruiting%' OR
							`reviews`.`text` LIKE '%nitrogen%' OR
							`reviews`.`text` LIKE '%oyster%' OR
							`reviews`.`text` LIKE '%scrumptious%' OR
							`reviews`.`text` LIKE '%flowers%' OR
							`reviews`.`text` LIKE '%fastidious%' OR
							`reviews`.`text` LIKE '%pasta%' OR
							`reviews`.`text` LIKE '%licking%' OR
							`reviews`.`text` LIKE '%leaves%' OR
							`reviews`.`text` LIKE '%sugar%' OR
							`reviews`.`text` LIKE '%cheeseburger%' OR
							`reviews`.`text` LIKE '%smelling%' OR
							`reviews`.`text` LIKE '%pigeon%' OR
							`reviews`.`text` LIKE '%eatables%' OR
							`reviews`.`text` LIKE '%tumble%' OR
							`reviews`.`text` LIKE '%rice%' OR
							`reviews`.`text` LIKE '%cheeses%' OR
							`reviews`.`text` LIKE '%sweet%' OR
							`reviews`.`text` LIKE '%fitch%' OR
							`reviews`.`text` LIKE '%glare%' OR
							`reviews`.`text` LIKE '%nutrient%' OR
							`reviews`.`text` LIKE '%round%' OR
							`reviews`.`text` LIKE '%nutritional%' OR
							`reviews`.`text` LIKE '%champagnes%' OR
							`reviews`.`text` LIKE '%seductive%' OR
							`reviews`.`text` LIKE '%soups%' OR
							`reviews`.`text` LIKE '%bleeding%' OR
							`reviews`.`text` LIKE '%rice%' OR
							`reviews`.`text` LIKE '%impious%' OR
							`reviews`.`text` LIKE '%alluring%' OR
							`reviews`.`text` LIKE '%tasting%' OR
							`reviews`.`text` LIKE '%slurpee%' OR
							`reviews`.`text` LIKE '%yummy%' OR
							`reviews`.`text` LIKE '%drinks%' OR
							`reviews`.`text` LIKE '%fuzzy%' OR
							`reviews`.`text` LIKE '%fabulous%' OR
							`reviews`.`text` LIKE '%cheese%' OR
							`reviews`.`text` LIKE '%dish%' OR
							`reviews`.`text` LIKE '%devastating%' OR
							`reviews`.`text` LIKE '%healed%' OR
							`reviews`.`text` LIKE '%capricious%' OR
							`reviews`.`text` LIKE '%hospitality%' OR
							`reviews`.`text` LIKE '%dimension%' OR
							`reviews`.`text` LIKE '%sensual%' OR
							`reviews`.`text` LIKE '%fished%' OR
							`reviews`.`text` LIKE '%calcium%' OR
							`reviews`.`text` LIKE '%whiskey%' OR
							`reviews`.`text` LIKE '%schedule%' OR
							`reviews`.`text` LIKE '%seriousness%' OR
							`reviews`.`text` LIKE '%egg%' OR
							`reviews`.`text` LIKE '%baking%' OR
							`reviews`.`text` LIKE '%toasty%' OR
							`reviews`.`text` LIKE '%doggie%' OR
							`reviews`.`text` LIKE '%yucky%' OR
							`reviews`.`text` LIKE '%shady%' OR
							`reviews`.`text` LIKE '%pigmies%' OR
							`reviews`.`text` LIKE '%cracking%' OR
							`reviews`.`text` LIKE '%hamburgers%' OR
							`reviews`.`text` LIKE '%yuppies%' OR
							`reviews`.`text` LIKE '%bean%' OR
							`reviews`.`text` LIKE '%pleasurable%' OR
							`reviews`.`text` LIKE '%pasties%' OR
							`reviews`.`text` LIKE '%climbing%' OR
							`reviews`.`text` LIKE '%mane%' OR
							`reviews`.`text` LIKE '%pigmies%' OR
							`reviews`.`text` LIKE '%wines%' OR
							`reviews`.`text` LIKE '%homemade%' OR
							`reviews`.`text` LIKE '%sausages%' OR
							`reviews`.`text` LIKE '%supercilious%' OR
							`reviews`.`text` LIKE '%eating%' OR
							`reviews`.`text` LIKE '%terrifying%' OR
							`reviews`.`text` LIKE '%treated%' OR
							`reviews`.`text` LIKE '%recipes%' OR
							`reviews`.`text` LIKE '%fabrics%' OR
							`reviews`.`text` LIKE '%tongue%' OR
							`reviews`.`text` LIKE '%chocolates%' OR
							`reviews`.`text` LIKE '%unexpected%' OR
							`reviews`.`text` LIKE '%supper%' OR
							`reviews`.`text` LIKE '%hot%' OR
							`reviews`.`text` LIKE '%doughnuts%' OR
							`reviews`.`text` LIKE '%moisture%' OR
							`reviews`.`text` LIKE '%embryo%' OR
							`reviews`.`text` LIKE '%cheeseburgers%' OR
							`reviews`.`text` LIKE '%delightful%' OR
							`reviews`.`text` LIKE '%walsh%' OR
							`reviews`.`text` LIKE '%seized%' OR
							`reviews`.`text` LIKE '%wave%' OR
							`reviews`.`text` LIKE '%picking%' OR
							`reviews`.`text` LIKE '%tooth%' OR
							`reviews`.`text` LIKE '%delectable%' OR
							`reviews`.`text` LIKE '%sexy%' OR
							`reviews`.`text` LIKE '%enticing%' OR
							`reviews`.`text` LIKE '%jiffy%' OR
							`reviews`.`text` LIKE '%syrupy%' OR
							`reviews`.`text` LIKE '%punching%' OR
							`reviews`.`text` LIKE '%lifestyle%' OR
							`reviews`.`text` LIKE '%stroking%' OR
							`reviews`.`text` LIKE '%tasteless%' OR
							`reviews`.`text` LIKE '%iced%' OR
							`reviews`.`text` LIKE '%cry%' OR
							`reviews`.`text` LIKE '%delicious%' OR
							`reviews`.`text` LIKE '%cocktails%' OR
							`reviews`.`text` LIKE '%sweet%' OR
							`reviews`.`text` LIKE '%chammy%' OR
							`reviews`.`text` LIKE '%chewing%' OR
							`reviews`.`text` LIKE '%schedules%' OR
							`reviews`.`text` LIKE '%stems%' OR
							`reviews`.`text` LIKE '%kicking%' OR
							`reviews`.`text` LIKE '%enjoy%' OR
							`reviews`.`text` LIKE '%captivating%' OR
							`reviews`.`text` LIKE '%speak%' OR
							`reviews`.`text` LIKE '%amusing%' OR
							`reviews`.`text` LIKE '%food%' OR
							`reviews`.`text` LIKE '%sweetish%' OR
							`reviews`.`text` LIKE '%martini%' OR
							`reviews`.`text` LIKE '%barbecue%' OR
							`reviews`.`text` LIKE '%yuppy%' OR
							`reviews`.`text` LIKE '%appetizer''s%' OR
							`reviews`.`text` LIKE '%gems%' OR
							`reviews`.`text` LIKE '%game%' OR
							`reviews`.`text` LIKE '%spicy%' OR
							`reviews`.`text` LIKE '%tasteful%' OR
							`reviews`.`text` LIKE '%addictive%' OR
							`reviews`.`text` LIKE '%onion%' OR
							`reviews`.`text` LIKE '%championship%' OR
							`reviews`.`text` LIKE '%sour%' OR
							`reviews`.`text` LIKE '%ladles%' OR
							`reviews`.`text` LIKE '%doctrines%' OR
							`reviews`.`text` LIKE '%damnable%' OR
							`reviews`.`text` LIKE '%cursing%' OR
							`reviews`.`text` LIKE '%fruits%' OR
							`reviews`.`text` LIKE '%scotch%' OR
							`reviews`.`text` LIKE '%slaughtered%' OR
							`reviews`.`text` LIKE '%shrill%' OR
							`reviews`.`text` LIKE '%behavioral%' OR
							`reviews`.`text` LIKE '%kissing%' OR
							`reviews`.`text` LIKE '%stripped%' OR
							`reviews`.`text` LIKE '%breakfast%' OR
							`reviews`.`text` LIKE '%brightness%' OR
							`reviews`.`text` LIKE '%litigiousness%' OR
							`reviews`.`text` LIKE '%glucose%' OR
							`reviews`.`text` LIKE '%salads%' OR
							`reviews`.`text` LIKE '%blurred%' OR
							`reviews`.`text` LIKE '%tunes%' OR
							`reviews`.`text` LIKE '%pollen%' OR
							`reviews`.`text` LIKE '%seize%' OR
							`reviews`.`text` LIKE '%flavorful%' OR
							`reviews`.`text` LIKE '%unpleasant%' OR
							`reviews`.`text` LIKE '%freeze%' OR
							`reviews`.`text` LIKE '%bizarre%' OR
							`reviews`.`text` LIKE '%rhythm%' OR
							`reviews`.`text` LIKE '%sauces%' OR
							`reviews`.`text` LIKE '%fruitful%' OR
							`reviews`.`text` LIKE '%educate%' OR
							`reviews`.`text` LIKE '%fried%' OR
							`reviews`.`text` LIKE '%halibuts%' OR
							`reviews`.`text` LIKE '%burger%' OR
							`reviews`.`text` LIKE '%cupcakes%' OR
							`reviews`.`text` LIKE '%tantalized%' OR
							`reviews`.`text` LIKE '%dinner%' OR
							`reviews`.`text` LIKE '%flower%' OR
							`reviews`.`text` LIKE '%suppers%' OR
							`reviews`.`text` LIKE '%academies%' OR
							`reviews`.`text` LIKE '%bribe%' OR
							`reviews`.`text` LIKE '%roasted%' OR
							`reviews`.`text` LIKE '%appliances%' OR
							`reviews`.`text` LIKE '%freezing%' OR
							`reviews`.`text` LIKE '%boar%' OR
							`reviews`.`text` LIKE '%markets%' OR
							`reviews`.`text` LIKE '%playoff%' OR
							`reviews`.`text` LIKE '%preposterous%' OR
							`reviews`.`text` LIKE '%fruition%' OR
							`reviews`.`text` LIKE '%drink%' OR
							`reviews`.`text` LIKE '%sugary%' OR
							`reviews`.`text` LIKE '%cuckoo%' OR
							`reviews`.`text` LIKE '%title%' OR
							`reviews`.`text` LIKE '%sarcastic%' OR
							`reviews`.`text` LIKE '%living%' OR
							`reviews`.`text` LIKE '%sobbing%' OR
							`reviews`.`text` LIKE '%bitter%' OR
							`reviews`.`text` LIKE '%champagne%' OR
							`reviews`.`text` LIKE '%fixture%' OR
							`reviews`.`text` LIKE '%bagels%' OR
							`reviews`.`text` LIKE '%fries%' OR
							`reviews`.`text` LIKE '%grainy%' OR
							`reviews`.`text` LIKE '%solitude%' OR
							`reviews`.`text` LIKE '%vicarious%' OR
							`reviews`.`text` LIKE '%seafood%' OR
							`reviews`.`text` LIKE '%haunting%' OR
							`reviews`.`text` LIKE '%cabbage%' OR
							`reviews`.`text` LIKE '%slapping%' OR
							`reviews`.`text` LIKE '%sipping%' OR
							`reviews`.`text` LIKE '%steak%' OR
							`reviews`.`text` LIKE '%stews%' OR
							`reviews`.`text` LIKE '%stingy%' OR
							`reviews`.`text` LIKE '%breathable%' OR
							`reviews`.`text` LIKE '%chilling%' OR
							`reviews`.`text` LIKE '%foods%' OR
							`reviews`.`text` LIKE '%wry%' OR
							`reviews`.`text` LIKE '%thermal%' OR
							`reviews`.`text` LIKE '%worshipped%' OR
							`reviews`.`text` LIKE '%chicken%' OR
							`reviews`.`text` LIKE '%vanilla%' OR
							`reviews`.`text` LIKE '%fighting%' OR
							`reviews`.`text` LIKE '%communicate%' OR
							`reviews`.`text` LIKE '%paperboy%' OR
							`reviews`.`text` LIKE '%pizza%' OR
							`reviews`.`text` LIKE '%outlets%' OR
							`reviews`.`text` LIKE '%sweetener%' OR
							`reviews`.`text` LIKE '%signal%' OR
							`reviews`.`text` LIKE '%washing%' OR
							`reviews`.`text` LIKE '%sweetened%' OR
							`reviews`.`text` LIKE '%beverage%' OR
							`reviews`.`text` LIKE '%berries%' OR
							`reviews`.`text` LIKE '%peas%' OR
							`reviews`.`text` LIKE '%desserts%' OR
							`reviews`.`text` LIKE '%regional%' OR
							`reviews`.`text` LIKE '%fresh%' OR
							`reviews`.`text` LIKE '%dreadful%' OR
							`reviews`.`text` LIKE '%incurious%' OR
							`reviews`.`text` LIKE '%spiced%' OR
							`reviews`.`text` LIKE '%somber%' OR
							`reviews`.`text` LIKE '%series%' OR
							`reviews`.`text` LIKE '%rancorous%' OR
							`reviews`.`text` LIKE '%swinging%' OR
							`reviews`.`text` LIKE '%appetizers%' OR
							`reviews`.`text` LIKE '%takeout%' OR
							`reviews`.`text` LIKE '%talents%' OR
							`reviews`.`text` LIKE '%wonderful%' OR
							`reviews`.`text` LIKE '%saturated%' OR
							`reviews`.`text` LIKE '%pigtails%' OR
							`reviews`.`text` LIKE '%cold%' OR
							`reviews`.`text` LIKE '%sniffing%' OR
							`reviews`.`text` LIKE '%foliage%' OR
							`reviews`.`text` LIKE '%porn%' OR
							`reviews`.`text` LIKE '%petals%' OR
							`reviews`.`text` LIKE '%horrific%' OR
							`reviews`.`text` LIKE '%exquisite%' OR
							`reviews`.`text` LIKE '%season%' OR
							`reviews`.`text` LIKE '%blowing%' OR
							`reviews`.`text` LIKE '%cleaned%' OR
							`reviews`.`text` LIKE '%juicy%' OR
							`reviews`.`text` LIKE '%impressionable%' OR
							`reviews`.`text` LIKE '%appetizing%' OR
							`reviews`.`text` LIKE '%playoffs%' OR
							`reviews`.`text` LIKE '%gratifying%' OR
							`reviews`.`text` LIKE '%soured%' OR
							`reviews`.`text` LIKE '%teach%' OR
							`reviews`.`text` LIKE '%feathered%' OR
							`reviews`.`text` LIKE '%highboy%' OR
							`reviews`.`text` LIKE '%paypal%' OR
							`reviews`.`text` LIKE '%powder%' OR
							`reviews`.`text` LIKE '%diet%' OR
							`reviews`.`text` LIKE '%luscious%' OR
							`reviews`.`text` LIKE '%dancing%' OR
							`reviews`.`text` LIKE '%lusciousness%' OR
							`reviews`.`text` LIKE '%soulful%' OR
							`reviews`.`text` LIKE '%cocktail%' OR
							`reviews`.`text` LIKE '%looney%' OR
							`reviews`.`text` LIKE '%lustful%' OR
							`reviews`.`text` LIKE '%celebrate%' OR
							`reviews`.`text` LIKE '%soaking%' OR
							`reviews`.`text` LIKE '%stale%' OR
							`reviews`.`text` LIKE '%cuisine%' OR
							`reviews`.`text` LIKE '%frozen%' OR
							`reviews`.`text` LIKE '%sultry%' OR
							`reviews`.`text` LIKE '%voracious%' OR
							`reviews`.`text` LIKE '%parsimonious%' OR
							`reviews`.`text` LIKE '%deliver%' OR
							`reviews`.`text` LIKE '%fruitcakes%' OR
							`reviews`.`text` LIKE '%learn%' OR
							`reviews`.`text` LIKE '%thrown%' OR
							`reviews`.`text` LIKE '%voltage%' OR
							`reviews`.`text` LIKE '%gloom%' OR
							`reviews`.`text` LIKE '%tablets%' OR
							`reviews`.`text` LIKE '%spite%' OR
							`reviews`.`text` LIKE '%learning%' OR
							`reviews`.`text` LIKE '%integrate%' OR
							`reviews`.`text` LIKE '%consume%' OR
							`reviews`.`text` LIKE '%embarrassing%' OR
							`reviews`.`text` LIKE '%fruity%' OR
							`reviews`.`text` LIKE '%jelly%' OR
							`reviews`.`text` LIKE '%flavors%' OR
							`reviews`.`text` LIKE '%deciduous%' OR
							`reviews`.`text` LIKE '%lizard%' OR
							`reviews`.`text` LIKE '%feisty%' OR
							`reviews`.`text` LIKE '%canned%' OR
							`reviews`.`text` LIKE '%stem%' OR
							`reviews`.`text` LIKE '%leger%' OR
							`reviews`.`text` LIKE '%league%' OR
							`reviews`.`text` LIKE '%investing%' OR
							`reviews`.`text` LIKE '%intriguing%' OR
							`reviews`.`text` LIKE '%hamburger%' OR
							`reviews`.`text` LIKE '%flowers%' OR
							`reviews`.`text` LIKE '%lobster%' OR
							`reviews`.`text` LIKE '%wax%' OR
							`reviews`.`text` LIKE '%optimizer%' OR
							`reviews`.`text` LIKE '%sticky%' OR
							`reviews`.`text` LIKE '%juice%' OR
							`reviews`.`text` LIKE '%rubbing%' OR
							`reviews`.`text` LIKE '%onion%' OR
							`reviews`.`text` LIKE '%biting%' OR
							`reviews`.`text` LIKE '%hormone%' OR
							`reviews`.`text` LIKE '%boiled%' OR
							`reviews`.`text` LIKE '%dough%' OR
							`reviews`.`text` LIKE '%lusciously%' OR
							`reviews`.`text` LIKE '%beguiling%' OR
							`reviews`.`text` LIKE '%seasons%' OR
							`reviews`.`text` LIKE '%nipple%' OR
							`reviews`.`text` LIKE '%cooking%' OR
							`reviews`.`text` LIKE '%litigious%' OR
							`reviews`.`text` LIKE '%tuna%' OR
							`reviews`.`text` LIKE '%amazing%' OR
							`reviews`.`text` LIKE '%steaks%' OR
							`reviews`.`text` LIKE '%polymer%' OR
							`reviews`.`text` LIKE '%crisp%' OR
							`reviews`.`text` LIKE '%croissants%' OR
							`reviews`.`text` LIKE '%splendid%' OR
							`reviews`.`text` LIKE '%budweiser''s%' OR
							`reviews`.`text` LIKE '%chummy%' OR
							`reviews`.`text` LIKE '%takeout''s%' OR
							`reviews`.`text` LIKE '%inspected%' OR
							`reviews`.`text` LIKE '%greasy%' OR
							`reviews`.`text` LIKE '%stance%' OR
							`reviews`.`text` LIKE '%tummy%' OR
							`reviews`.`text` LIKE '%seasoning%' OR
							`reviews`.`text` LIKE '%conference%' OR
							`reviews`.`text` LIKE '%hilarious%' OR
							`reviews`.`text` LIKE '%bathed%' OR
							`reviews`.`text` LIKE '%lustrous%' OR
							`reviews`.`text` LIKE '%eat%' OR
							`reviews`.`text` LIKE '%swell%' OR
							`reviews`.`text` LIKE '%examine%' OR
							`reviews`.`text` LIKE '%noise%' OR
							`reviews`.`text` LIKE '%toothed%' OR
							`reviews`.`text` LIKE '%watery%' OR
							`reviews`.`text` LIKE '%brainteaser%' OR
							`reviews`.`text` LIKE '%breathtaking%' OR
							`reviews`.`text` LIKE '%fanboy%' OR
							`reviews`.`text` LIKE '%bread%' OR
							`reviews`.`text` LIKE '%salsa%' OR
							`reviews`.`text` LIKE '%driving%' OR
							`reviews`.`text` LIKE '%bosom%' OR
							`reviews`.`text` LIKE '%acid%' OR
							`reviews`.`text` LIKE '%licentious%' OR
							`reviews`.`text` LIKE '%sweetbreads%' OR
							`reviews`.`text` LIKE '%pizzas%' OR
							`reviews`.`text` LIKE '%tasty%' OR
							`reviews`.`text` LIKE '%burgers%' OR
							`reviews`.`text` LIKE '%sensuous%' OR
							`reviews`.`text` LIKE '%year%' OR
							`reviews`.`text` LIKE '%blueberries%' OR
							`reviews`.`text` LIKE '%sucking%' OR
							`reviews`.`text` LIKE '%silky%' OR
							`reviews`.`text` LIKE '%pugilistic%' OR
							`reviews`.`text` LIKE '%dessert%' OR
							`reviews`.`text` LIKE '%harvested%' OR
							`reviews`.`text` LIKE '%fusty%' OR
							`reviews`.`text` LIKE '%liquor%' OR
							`reviews`.`text` LIKE '%buying%' OR
							`reviews`.`text` LIKE '%manners%' OR
							`reviews`.`text` LIKE '%carbon%' OR
							`reviews`.`text` LIKE '%tantalizing%' OR
							`reviews`.`text` LIKE '%demeaning%' OR
							`reviews`.`text` LIKE '%cutter%' OR
							`reviews`.`text` LIKE '%avaricious%' OR
							`reviews`.`text` LIKE '%flavor%' OR
							`reviews`.`text` LIKE '%pleasuring%' OR
							`reviews`.`text` LIKE '%ministries%' OR
							`reviews`.`text` LIKE '%recipe%' OR
							`reviews`.`text` LIKE '%flowering%' OR
							`reviews`.`text` LIKE '%mushroom%' OR
							`reviews`.`text` LIKE '%cheesecakes%' OR
							`reviews`.`text` LIKE '%wrappers%' OR
							`reviews`.`text` LIKE '%sweets%' OR
							`reviews`.`text` LIKE '%toast%' OR
							`reviews`.`text` LIKE '%broomstick%' OR
							`reviews`.`text` LIKE '%brisk%' OR
							`reviews`.`text` LIKE '%fascinate%' OR
							`reviews`.`text` LIKE '%salt%' OR
							`reviews`.`text` LIKE '%downs%' OR
							`reviews`.`text` LIKE '%tournament%' OR
							`reviews`.`text` LIKE '%explore%' OR
							`reviews`.`text` LIKE '%sauce%' OR
							`reviews`.`text` LIKE '%flowery%' OR
							`reviews`.`text` LIKE '%stings%' OR
							`reviews`.`text` LIKE '%semiconscious%' OR
							`reviews`.`text` LIKE '%owning%' OR
							`reviews`.`text` LIKE '%swabs%' OR
							`reviews`.`text` LIKE '%tones%' OR
							`reviews`.`text` LIKE '%snacks%' OR
							`reviews`.`text` LIKE '%disturbing%' OR
							`reviews`.`text` LIKE '%demeanor%' OR
							`reviews`.`text` LIKE '%irritating%' OR
							`reviews`.`text` LIKE '%prettifying%' OR
							`reviews`.`text` LIKE '%laughable%' OR
							`reviews`.`text` LIKE '%wine%' OR
							`reviews`.`text` LIKE '%cured%' OR
							`reviews`.`text` LIKE '%pastries%' OR
							`reviews`.`text` LIKE '%multifarious%' OR
							`reviews`.`text` LIKE '%oats%' OR
							`reviews`.`text` LIKE '%hungry%' OR
							`reviews`.`text` LIKE '%shortbread%' OR
							`reviews`.`text` LIKE '%spice%' OR
							`reviews`.`text` LIKE '%distracting%' OR
							`reviews`.`text` LIKE '%grape%' OR
							`reviews`.`text` LIKE '%sweetbread%' OR
							`reviews`.`text` LIKE '%pernicious%' OR
							`reviews`.`text` LIKE '%dye%' OR
							`reviews`.`text` LIKE '%grapes%' OR
							`reviews`.`text` LIKE '%clumsy%' OR
							`reviews`.`text` LIKE '%tone%' OR
							`reviews`.`text` LIKE '%sinuous%' OR
							`reviews`.`text` LIKE '%ceramic%' OR
							`reviews`.`text` LIKE '%pastry%' OR
							`reviews`.`text` LIKE '%delicious%' OR
							`reviews`.`text` LIKE '%cooks%' OR
							`reviews`.`text` LIKE '%veggies%' OR
							`reviews`.`text` LIKE '%pancakes%' OR
							`reviews`.`text` LIKE '%refreshing%' OR
							`reviews`.`text` LIKE '%peppercorns%' OR
							`reviews`.`text` LIKE '%tapeworm%' OR
							`reviews`.`text` LIKE '%tubular%' OR
							`reviews`.`text` LIKE '%stinger%' OR
							`reviews`.`text` LIKE '%oven%' OR
							`reviews`.`text` LIKE '%lethal%' OR
							`reviews`.`text` LIKE '%occlusive%' OR
							`reviews`.`text` LIKE '%ringlet%' OR
							`reviews`.`text` LIKE '%ferocious%' OR
							`reviews`.`text` LIKE '%dishes%' OR
							`reviews`.`text` LIKE '%cakes%' OR
							`reviews`.`text` LIKE '%billing%' OR
							`reviews`.`text` LIKE '%crackers%' OR
							`reviews`.`text` LIKE '%grill%' OR
							`reviews`.`text` LIKE '%boozy%' OR
							`reviews`.`text` LIKE '%experiencing%' OR
							`reviews`.`text` LIKE '%temper%' OR
							`reviews`.`text` LIKE '%shimmy%' OR
							`reviews`.`text` LIKE '%hoarse%' OR
							`reviews`.`text` LIKE '%sulfate%' OR
							`reviews`.`text` LIKE '%taste%' OR
							`reviews`.`text` LIKE '%omelets%' OR
							`reviews`.`text` LIKE '%fascinating%' OR
							`reviews`.`text` LIKE '%toothless%' OR
							`reviews`.`text` LIKE '%flavored%' OR
							`reviews`.`text` LIKE '%puddings%' OR
							`reviews`.`text` LIKE '%knotted%' OR
							`reviews`.`text` LIKE '%touching%' OR
							`reviews`.`text` LIKE '%peppers%' OR
							`reviews`.`text` LIKE '%danes%' OR
							`reviews`.`text` LIKE '%cereal%' OR
							`reviews`.`text` LIKE '%tuneful%' OR
							`reviews`.`text` LIKE '%resin%' OR
							`reviews`.`text` LIKE '%popcorn%' OR
							`reviews`.`text` LIKE '%flavorless%' OR
							`reviews`.`text` LIKE '%shrimp%' OR
							`reviews`.`text` LIKE '%downs%' OR
							`reviews`.`text` LIKE '%cooked%' OR
							`reviews`.`text` LIKE '%donuts%' OR
							`reviews`.`text` LIKE '%toothsome%' OR
							`reviews`.`text` LIKE '%sausage%' OR
							`reviews`.`text` LIKE '%jumpy%' OR
							`reviews`.`text` LIKE '%apron%' OR
							`reviews`.`text` LIKE '%exciting%' OR
							`reviews`.`text` LIKE '%fruit%' OR
							`reviews`.`text` LIKE '%riveting%' OR
							`reviews`.`text` LIKE '%scoop%' OR
							`reviews`.`text` LIKE '%interesting%' OR
							`reviews`.`text` LIKE '%drinking%' OR
							`reviews`.`text` LIKE '%tequila%' OR
							`reviews`.`text` LIKE '%face%' OR
							`reviews`.`text` LIKE '%organic%' OR
							`reviews`.`text` LIKE '%offerings%' OR
							`reviews`.`text` LIKE '%custards%' OR
							`reviews`.`text` LIKE '%season''s%' OR
							`reviews`.`text` LIKE '%glue%' OR
							`reviews`.`text` LIKE '%toothy%' OR
							`reviews`.`text` LIKE '%baked%' OR
							`reviews`.`text` LIKE '%mocked%' OR
							`reviews`.`text` LIKE '%custard%' OR
							`reviews`.`text` LIKE '%leaf%' OR
							`reviews`.`text` LIKE '%womb%' OR
							`reviews`.`text` LIKE '%week%' OR
							`reviews`.`text` LIKE '%mint%' OR
							`reviews`.`text` LIKE '%feathering%' OR
							`reviews`.`text` LIKE '%banquets%' OR
							`reviews`.`text` LIKE '%wholesome%' OR
							`reviews`.`text` LIKE '%oils%' OR
							`reviews`.`text` LIKE '%intoxicating%' OR
							`reviews`.`text` LIKE '%contumacious%' OR
							`reviews`.`text` LIKE '%heal%' OR
							`reviews`.`text` LIKE '%chasing%' OR
							`reviews`.`text` LIKE '%aromatic%' OR
							`reviews`.`text` LIKE '%snacked%' OR
							`reviews`.`text` LIKE '%salty%' OR
							`reviews`.`text` LIKE '%eater%' OR
							`reviews`.`text` LIKE '%wingnut%' OR
							`reviews`.`text` LIKE '%smoky%' OR
							`reviews`.`text` LIKE '%stealing%' OR
							`reviews`.`text` LIKE '%buffets%' OR
							`reviews`.`text` LIKE '%massage%' OR
							`reviews`.`text` LIKE '%vegetables%' OR
							`reviews`.`text` LIKE '%eaten%' OR
							`reviews`.`text` LIKE '%nutrients%' OR
							`reviews`.`text` LIKE '%appetizer%' OR
							`reviews`.`text` LIKE '%creations%' OR
							`reviews`.`text` LIKE '%behave%' OR
							`reviews`.`text` LIKE '%pizzazz%' OR
							`reviews`.`text` LIKE '%chewy%' OR
							`reviews`.`text` LIKE '%kiddie%' OR
							`reviews`.`text` LIKE '%plank%' OR
							`reviews`.`text` LIKE '%donut%' OR
							`reviews`.`text` LIKE '%droplet%' OR
							`reviews`.`text` LIKE '%brands%' OR
							`reviews`.`text` LIKE '%angles%' OR
							`reviews`.`text` LIKE '%bender%' OR
							`reviews`.`text` LIKE '%nectar%' OR
							`reviews`.`text` LIKE '%bender%' OR
							`reviews`.`text` LIKE '%budweiser%' OR
							`reviews`.`text` LIKE '%scotch%' OR
							`reviews`.`text` LIKE '%chips%' OR
							`reviews`.`text` LIKE '%burger%' OR
							`reviews`.`text` LIKE '%cake%' OR
							`reviews`.`text` LIKE '%fruited%' OR
							`reviews`.`text` LIKE '%configurations%' OR
							`reviews`.`text` LIKE '%dining%' OR
							`reviews`.`text` LIKE '%scary%' OR
							`reviews`.`text` LIKE '%hunted%' OR
							`reviews`.`text` LIKE '%cherries%' OR
							`reviews`.`text` LIKE '%milked%' OR
							`reviews`.`text` LIKE '%waffles%' OR
							`reviews`.`text` LIKE '%roast%' OR
							`reviews`.`text` LIKE '%adorable%' OR
							`reviews`.`text` LIKE '%chaffinches%' OR
							`reviews`.`text` LIKE '%stuffing%' OR
							`reviews`.`text` LIKE '%pudding%'
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
