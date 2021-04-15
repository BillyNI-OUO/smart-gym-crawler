import requests
import json
import re
from src import constants

from src.crawler import decode 


from src.crawler.place import place
from src.crawler.review import review

def pretty(obj):
    import pprint
    with open('sample.json', "w")as f:
        pprint.pprint(obj, f)

def nearby2(location=(22.0108477, 120.7440363), query_size=3, query_times = 1, keyword = constants.KEYWORD):
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


def reviews(cid, max_query_times=1, query_size=199):
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
        for row in reviews_data:
            review = decode.reviews(row, cid)

            if review == None:
                break;
            review_info_list.append(review)

        if len(reviews_data) < query_size:
            break

    return review_info_list