from selenium import webdriver

import requests
from bs4 import BeautifulSoup
#import src.constants as constants
from selenium import webdriver

import time
import re
import sys

con = connector()

con.init_db()
def get_cid(keyword):
	op = webdriver.ChromeOptions()
	op.add_argument('--headless')
	chrome = webdriver.Chrome('./chromedriver',options=op)


	#chrome.find_element_by_xpath(f"/html/body/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[1]/div[1]/div/a").click()


	#HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

	url = "https://www.google.com/maps/search/"
	keyword = "三燔"

	#resp = requests.get(url+keyword, allow_redirects=True, headers = HEADERS)
	#print(resp.text)
	chrome.get(url+keyword)
	time.sleep(2)
	soup = BeautifulSoup(chrome.page_source, "html.parser")
	results = soup.find_all("a" , class_="a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd")
	link = results[0].get("href")
	cid = int(re.search(r":0x\w*", link).group()[1:], 16)
	print(cid)
	#/html/body/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[1]/div[1]/div/a
	#a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd


lastupdate = con.query(f"SELECT `lastupdate` FROM `time` ORDER BY `id` DESC LIMIT 1")[0]['lastupdate']
ll = con.get_feedback_missing_place()
newlist = list(filter(lambda x : x[1]>lastupdate, ll))
cid_list = []
for i in newlist:
	keyword = i[0]
	cid_list.append(get_cid(keyword))

for cid in cid_list:
	place = crawler.query.places(cid)
	con.insert_place(place)
	review_list = crawler.query.reviews(places.cid_1, place.cid_2)
	con.inser_reviews(review_list)



