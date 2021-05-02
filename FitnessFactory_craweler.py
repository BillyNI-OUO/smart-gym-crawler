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
url='https://www.fitnessfactory.com.tw/locations'
##map_url='https://www.google.com.tw/maps/@23.546162,120.6402133,8z?hl=zh-TW'
driver.get(url)
request=req.Request(url, headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
        })
with req.urlopen(request) as response:
	data=response.read().decode("utf-8")

##將地址都爬下來
gym_locations=[]
time.sleep(2)
select = Select(driver.find_element_by_id('region'))
for i in range(1,6):
	select.select_by_index(i)
	time.sleep(2)
	sub_select = Select(driver.find_element_by_id('locations'))
	
	for j in range(len(sub_select.options)):
		sub_select.select_by_index(j)
		time.sleep(2)
		soup = BeautifulSoup(driver.page_source, "html.parser")
		
		results = soup.find("h4", class_ = "js--location").getText()
		re.sub(r"^\s+", "", results)
		print(results)
		gym_locations.append(results)
		results = soup.find("p", class_ = "js--address").getText()	
		print(results)


with open('fitnessfactory_locations.txt','a') as fp:
	for lc in gym_locations:
		fp.write(str(lc)+"\n")
driver.quit()

##輸入google map查詢cid