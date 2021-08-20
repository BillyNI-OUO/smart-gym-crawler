import requests
import json
import re
import sys
from src import constants
from src.crawler import decode 
from src.crawler.place import place
from src.crawler.review import review
from lxml import etree
from bs4 import BeautifulSoup

def pretty(obj):
    import pprint
    with open('sample.json', "w")as f:
        pprint.pprint(obj, f)

def nearby2(location=(22.0108477, 120.7440363), query_size=constants.QUERY_SIZE, query_times = 1, keyword = constants.KEYWORD):
    """
    Queary the nearby place without APIKEY
    Parameter:
    location    : (latitude, longitude)
    query_size  : the size of query per time
    query_times : query how many times
    keyword     : the keyword you want to search, define in src.crawler.constant.KEYWORD
    """

    lng, lat = location
    place_info_list = []

    for cnt in range(query_times):
        url = constants.nearby2_url(lat, lng, cnt, query_size, keyword)
        response = requests.request("GET", url, headers=constants.HEADERS)
        raw_text = response.text.encode('utf8')[4:]
        data = json.loads(raw_text)
        for i in range(1, len(data[0][1])):
            place_info_list.append(decode.nearby2(data, i))
    
    return place_info_list


def reviews(cid, max_query_times=5, query_size=199):
    """
    Queary the reviews by the place's cid
    Parameter:
    cid             : The cid of place
    max_query_times : Maximum times to query
    query_size      : The size of query per time
    """

    review_info_list = []
    for i in range(max_query_times):
        url = constants.reviews_url(cid, i, query_size)
        response = requests.request("GET", url, headers=constants.HEADERS)
        raw_text = response.text.encode('utf8')[4:]
        data = json.loads(raw_text)

        reviews_data = data[2]
        if reviews_data == None:
            break
        for row in reviews_data:
            review = decode.reviews(row, cid)

            if review == None:
                break
            review_info_list.append(review)

        if len(reviews_data) < query_size:
            break

    return review_info_list

def check_business(cid):
    #url = "https://www.google.com/maps/place/data=!3m1!4b1!4m13!1m6!3m5!1s0x3442abd074c4b9a5:0x84807da2fa429!2z5a2U6Zm15LiA6Zq76Zue!8m2!3d25.0409184!4d121.5469845!3m5!1s0x3442abd074c4b9a5:0x84807da2fa429!8m2!3d25.0409184!4d121.5469845!15sCg_lrZTpmbXkuIDpmrvpm55aFSIT5a2UIOmZtSDkuIAg6Zq7IOmbnpIBEWtvcmVhbl9yZXN0YXVyYW50mgEkQ2hkRFNVaE5NRzluUzBWSlEwRm5TVVF3Y0hZdFVISkJSUkFC"
    #url = 'https://www.google.com/maps/place/%E5%AD%94%E9%99%B5%E4%B8%80%E9%9A%BB%E9%9B%9E/@25.0409916,121.4570335,15z/data=!3m1!4b1!4m13!1m6!3m5!1s0x3442abd074c4b9a5:0x84807da2fa429!2z5a2U6Zm15LiA6Zq76Zue!8m2!3d25.0409184!4d121.5469845!3m5!1s0x3442abd074c4b9a5:0x84807da2fa429!8m2!3d25.0409184!4d121.5469845!15sCg_lrZTpmbXkuIDpmrvpm55aFSIT5a2UIOmZtSDkuIAg6Zq7IOmbnpIBEWtvcmVhbl9yZXN0YXVyYW50mgEkQ2hkRFNVaE5NRzluUzBWSlEwRm5TVVF3Y0hZdFVISkJSUkFC'
    try:
        url = constants.place_url(cid)
        response = requests.request("GET", url, headers=constants.HEADERS)
    #print(response.content)
        raw_text = response.text.encode('utf8')[4:]
        data = json.loads(raw_text)
    #with open('buisnesssd.json', 'w+') as fp:
    #    json.dump(data, fp, ensure_ascii=False, indent=4)
    #print(data)
    #print(re.search(r'停業',str(data)).group(0))
    #selector = etree.HTML(raw_text)
    #a = selector.xpath('//*[@id="pane"]/div/div[1]/div/div/div[7]/div[2]/div[1]/div/div[1]/span[1]/span[1]//text()')
    #print(a)

    #soup = BeautifulSoup(raw_text, 'html.parser')
    #a = soup.find_all(class_='LJKBpe-Tswv1b-text')
    #print(a)
    #a = soup.find_all(jstache='')
    #print(a)

    #//*[@id="pane"]/div/div[1]/div/div/div[7]/div[2]/div[1]
    #//*[@id="pane"]/div/div[1]/div/div/div[7]/div[2]/div[1]
    
        return decode.buisness(data)
    except Exception as e:
        sys.stderr.write(str(e)+"\n");
        return 0