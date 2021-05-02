import requests
from bs4 import BeautifulSoup
import src.constants as constants
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re
import sys

options = Options()
options.add_argument("--disable-notifications")
chrome = webdriver.Chrome('/mnt/c/Users/小傑/Desktop/chromedriver_win32/chromedriver.exe', chrome_options=options)


links = []
url = "https://www.worldgymtaiwan.com/locations"
chrome.maximize_window()
chrome.get(url)
time.sleep(3)
for i in range(1, 17):
	chrome.find_element_by_xpath(f"/html/body/div/main/div/div[2]/div[2]/div[1]/div[2]/ul/li[{i}]").click()
	time.sleep(2)
	soup = BeautifulSoup(chrome.page_source, "html.parser")
	
	results = soup.find_all("i", class_ = "icon-location")

	for result in results:
		next_node = result.find_next_siblings("a")
		link = next_node[0].get("href")
		links.append(link)

	time.sleep(1)

print(links)
chrome.quit()
"""
with open('links.txt', "w") as fp:
	for i in links:
		fp.writelines(i+"\n")


links = []
with open('links.txt', 'r') as fp:
	lines = fp.readlines()
	for line in lines:
		links.append(line.split("\n")[0])

"""

def revertShortLink(url):
	resp = requests.head(url, allow_redirects=True, headers = constants.HEADERS)
	return resp.url

cid = []
for link in links:
	link = revertShortLink(link)
	#print(link)
	try:#print(re.search(r":0x\w*", link).group())
		cid.append(int(re.search(r":0x\w*", link).group()[1:], 16))
	except Exception as e:
		sys.stderr.write(str(e)+"\n")

print(cid)
print(len(cid))
with open('word_gym_cid.txt', 'w') as fp:
	for i in cid:
		fp.write(str(i)+"\n")
"""

for i in links:
	print(i)	
	print(revertShortLink(i))




res = requests.request("GET", url, headers = constants.HEADERS)
#print(res.text)
soup = BeautifulSoup(res.text, "html.parser")
#print(soup.prettify())
#print(soup.find_all("i", class_ = "icon-location"))
results = soup.find_all("i", class_ = "icon-location")
links = []
for result in results:
	next_node = result.find_next_siblings("a")
	link = next_node[0].get("href")
	links.append(link)

"""