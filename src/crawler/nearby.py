import requests
import json
from src.crawler import constants
from src.crawler.place import place
from src.crawler import decode 
def pretty(obj):
    import pprint
    with open('sample.json', "w")as f:
        pprint.pprint(obj, f)

def nearby2(location=(22.0108477, 120.7440363), query_size=3, type='餐廳'):
    lng, lat = location
    place_info_list = []
    for cnt in range(1):
        url = constants.nearby2_url(lat, lng, cnt, query_size)
        response = requests.request("GET", url, headers=constants.HEADERS)
        raw_text = response.text.encode('utf8')[4:]
        data = json.loads(raw_text)
        #raw_text = raw_text.decode('unicode-escape')
        #pretty(data)
        for i in range(1, len(data[0][1])):
           place_info_list.append(decode.nearby2(data, i))
    return place_info_list
