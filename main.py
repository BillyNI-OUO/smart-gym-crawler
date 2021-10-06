#from src.crawler import *
import src
import src.crawler as crawler

#import src.sql as sql
from src.sql.connector import connector
from datetime import datetime

con = connector()

con.init_db()

"""
l = crawler.grid.search_nearby2(lat_range=(21.9, 22), lng_range=(120.8, 121))
for i in l:
	
	con.insert_place(i)
	print(i)
	ll = crawler.query.reviews((i.cid_1, i.cid_2))
	con.insert_reviews(ll)
print(ll[0])
"""
"""
cor_list = crawler.coordinate.get_coordinate('./coordinates/台中.txt')
con = connector()

con.init_db()

l = crawler.grid.search_nearby2(cor_list[2][0], cor_list[2][1])
for i in l:
	print(i)
	if con.insert_place(i):
		ll = crawler.query.reviews((i.cid_1, i.cid_2))
		con.insert_reviews(ll)
"""
"""
count = 1
cor_list = crawler.coordinate.taiwan('./coordinates/台灣.txt')
for cor in cor_list[5:]:
	place_list = crawler.query.nearby2(location = cor)
	for place in place_list:
		if place == None:
			break
		if con.insert_place(place):
			print(count)
			count += 1
			print(place)
			
			review_list = crawler.query.reviews((place.cid_1, place.cid_2))
			con.insert_reviews(review_list)
"""
"""
field = ['cid_1', 'cid']
con.download_query(field = field, table = 'place', predicate = "WHERE cid_1 = 1445430307838188779", filepath="")
"""
'''
placeList = con.query_place(['cid_1', 'cid'])
#print(placeList)
for place in placeList[160067:]:
	#print(place[1])
	tag = crawler.query.check_business(place[1])
	#print('tag:'+str(tag))
	con.update_buisness(place[1], tag)
	ll = crawler.query.reviews((0,place[1]))
	#print(ll)
	con.insert_reviews(ll)

#0x3442a9023d1c224d:0x23c54d0c79a1a1d7
'''
'''
#38457636
con.execute("""
REPLACE INTO `aspect_ratings` (
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
;""")
'''

#lastId = con.get_lastId()[0][0]
#con.text_classify(lastId)
'''
l = crawler.query.nearby2()
ll = crawler.query.reviews((l[0].cid_1, l[0].cid_2))
print(ll[0].time)
now = datetime.now()
print(now)
print(datetime.strptime(ll[0].time, "%Y-%m-%d %H:%M:%S") > datetime.now())
'''
#con.update_user_rating_total()

"""
Place = crawler.query.place(4438821563071615652)
print(Place)

con.insert_place(Place)
ll = crawler.query.reviews((Place.cid_1, Place.cid_2))
con.insert_reviews(ll)
"""
"""
lastupdate = con.query(f"SELECT `lastupdate` FROM `time` ORDER BY `id` DESC LIMIT 1")[0]['lastupdate']
ll = con.get_feedback_missing_place()
newlist = list(filter(lambda x : x[1]>lastupdate, ll))
for i in newlist:
	i[0]
"""
con.update_user_rating_total()