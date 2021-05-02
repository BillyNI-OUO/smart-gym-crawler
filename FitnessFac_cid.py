from selenium import webdriver
import urllib.request as req
import bs4,sys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time
from bs4 import BeautifulSoup
import re
options = Options()
options.add_argument("--disable-notifications")
driver=webdriver.Chrome('/mnt/c/Users/user/Desktop/final_pro/cowel/Selenium/chromedriver.exe', chrome_options=options)
url='https://www.google.com.tw/maps/@23.546162,120.6402133,8z?hl=zh-TW'
##map_url='https://www.google.com.tw/maps/@23.546162,120.6402133,8z?hl=zh-TW'
driver.get(url)
request=req.Request(url, headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
        })
with req.urlopen(request) as response:
	data=response.read().decode("utf-8")

i=0
search=[]
with open('fitnessfactory_locations.txt','r') as fp:
	lines=fp.readlines()
	for line in lines:
		if line=='\n':
			pass
		else:
			location='健身工廠 '+line.lstrip().strip('\n')
			if location not in search and "預售中" not in location:
				search.append(location)
"""
print(len(search))
for i in search:
	print(i)

time.sleep(2)
element=driver.find_element_by_id("searchboxinput")
element.send_keys("健身工廠 嘉義廠")

button=driver.find_element_by_id("searchbox-searchbutton")
button.click()


time.sleep(2)
element.clear()
element=driver.find_element_by_id("searchboxinput")
element.send_keys("健身工廠 博愛廠")

button=driver.find_element_by_id("searchbox-searchbutton")
button.click()
"""
for i in search:
	print(i)
links=[]
cids=[]
time.sleep(4)
element=driver.find_element_by_id("searchboxinput")
button=driver.find_element_by_id("searchbox-searchbutton")
for s in search:
	time.sleep(10)
	try:
		close_button = driver.find_element_by_xpath(f"/html/body/jsl/div[3]/div[8]/div/div/div/div[1]/div/div/div/button")
		if close_button != None:
			close_button.click()
	except Exception as e:
		sys.stderr.write(str(e)+"\n")
		time.sleep(5)
	element.send_keys(s)
	time.sleep(4)
	button.click()
	time.sleep(6)
	##links.append(driver.current_url)
	print(driver.current_url)
	links.append(driver.current_url)
	try:
		cid=int(re.search(r":0x\w*",driver.current_url).group()[1:], 16)
		if cid not in cids:
			print(s)
			print(cid)
			cids.append(cid)
	except Exception as e:
		sys.stderr.write(str(e)+"\n")
	time.sleep(5)
	element.clear()
	time.sleep(5)
"""
cid=[]
print(len(links))
for link in links:
	try:
		cid.append(int(re.search(r"s0x\w*", link).group()[1:], 16))
	except Exception as e:
		sys.stderr.write(str(e)+"\n")
"""
for c in cids:
	print(c)
print(len(cids))
with open('FitnessFac_cid.txt', 'w') as fp:
	for i in cids:
		fp.write(str(i)+"\n")
with open('fitnessfactory_url.txt','w') as fp:
	for i in links:
		fp.write(str(i)+"\n")
