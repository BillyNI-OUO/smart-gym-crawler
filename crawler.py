# -*- coding: utf-8 -*-
# This file is based on 陳閒吉's code, thanks a lot

import logging
import requests
import json
import re

# APIKEY = 'AIzaSyCjtEh9nPvAskGG99YY8oQOKv2d2v-J-vM' # pp.pp253
# APIKEY = 'AIzaSyDDmEI0V2poJKXXuwviyiRXqmRF-hH7SeY' # 陳閒吉
# APIKEY = 'AIzaSyBiCf6PJjAi6gDhoMObgOuLyzD9Uhrubyc'  # nthu.acolab
# APIKEY = 'AIzaSyAie5EFbKi2Wfg0C0DPiRAthPD2gTD5_9s' #ieem202100 離散數學
# APIKEY = 'AIzaSyA0n3vya8D2qcx9tuVctQn1JWEQdn7Yc18' #comieem519000 組合最佳化
# APIKEY = 'AIzaSyCG9dBk6rP1xatlScvP-Mz8sRGGtf1s-sk' #ieem314000 資料結構
APIKEY = 'AIzaSyAie5EFbKi2Wfg0C0DPiRAthPD2gTD5_9s'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}


APIKEY_CALLS = 0


def pretty(obj):
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(obj)


def to_place_info_factory(place_info):
    keys = ['place_id', 'name', 'rating', 'user_ratings_total']

    if not all(key in place_info for key in keys):
        # pretty(place_info)
        raise Exception('Some keys lost.')

    filtered_place_info = {key: place_info[key] for key in keys}
    if 'price_level' in place_info:
        filtered_place_info['price_level'] = place_info['price_level']
    if 'formatted_address' in place_info:
        filtered_place_info['formatted_address'] = place_info['formatted_address']
    if 'types' in place_info:
        filtered_place_info['types'] = place_info['types']
    if 'geometry' in place_info:
        filtered_place_info['lng'] = place_info['geometry']['location']['lng']
        filtered_place_info['lat'] = place_info['geometry']['location']['lat']
    return filtered_place_info


def query_place_info(query_text, type='restaurant'):
    global APIKEY_CALLS

    # get place_id
    url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?key={APIKEY}&query={query_text}&type={type}&language=zh-TW&region=tw'
    APIKEY_CALLS += 1
    print('apicalls:', APIKEY_CALLS)
    response = requests.REQUEST("GET", url, headers=HEADERS)
    data = json.loads(response.text.encode('utf8'))

    assert len(data["results"]) > 0, f'No matched stores: {query_text}.'

    place_info = data["results"][0]

    filtered_place_info = to_place_info_factory(place_info)

    return filtered_place_info


def query_multiple_place_info(query_text, max_query_times=100, type='restaurant'):
    global APIKEY_CALLS

    place_info_list = []
    next_page_token = None
    url = None

    for i in range(max_query_times):
        if i == 0:
            url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?key={APIKEY}&query={query_text}&type={type}&language=zh-TW&region=tw'
        else:
            url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?key={APIKEY}&pagetoken={next_page_token}'

        APIKEY_CALLS += 1
        print('apicalls:', APIKEY_CALLS)
        response = requests.request("GET", url, headers=HEADERS)
        # to avoid the first 5 unwanted char
        # data = json.loads(response.text.encode('utf8')[4:])
        data = json.loads(response.text.encode('utf8'))
        next_page_token = data['next_page_token'] if 'next_page_token' in data else None

        for place_info in data['results']:
            filtered_place_info = to_place_info_factory(place_info)
            place_info_list.append(filtered_place_info)

        if next_page_token is None:
            break
        print(next_page_token)
    print(query_text, len(place_info_list))
    return place_info_list


def query_place_info_by_cid(cid):
    global APIKEY_CALLS

    url = f'https://maps.googleapis.com/maps/api/place/details/json?cid={cid}&key={APIKEY}&language=zh-TW&region=tw'

    APIKEY_CALLS += 1
    print('apicalls:', APIKEY_CALLS)

    response = requests.request("GET", url, headers=HEADERS)
    data = json.loads(response.text.encode('utf8'))

    try:
        place_info = data["result"]
    except Exception as e:
        print(data)
        raise e

    filtered_place_info = to_place_info_factory(place_info)

    return filtered_place_info


def query_cid_by_place_id(place_id):
    global APIKEY_CALLS

    # get cid
    url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={APIKEY}&language=zh-TW&fields=url'
    APIKEY_CALLS += 1
    print('apicalls:', APIKEY_CALLS)
    response = requests.request("GET", url, headers=HEADERS, data={})
    data = json.loads(response.text.encode('utf8'))
    line = data["result"]["url"]
    cid = re.search("[0-9]+", line).group(0)
    return cid


def query_reviews(cid, max_query_times=100, item_per_page=199):
    review_id = []
    rating = []
    time = []
    text = []
    author_name = []
    author_id = []  # customized
    hide_id = None

    for i in range(max_query_times):
        try:
            url = f'https://www.google.com/maps/preview/review/listentitiesreviews?authuser=0&hl=zh-TW&gl=tw&pb=!1m2!1y0!2y{cid}!2m2!1i{item_per_page * i}!2i{item_per_page}!'

            response = requests.request("GET", url, headers=HEADERS)
            # to avoid the first 5 unwanted char
            data = json.loads(response.text.encode('utf8')[4:])

            reviews_data = data[2]
            if reviews_data is None:
                break

            for row in reviews_data:
                if row[3] is None:
                    text.append(None)
                else:
                    text.append(row[3])
                review_id.append(row[10])
                rating.append(row[4])
                author_name.append(row[0][1])
                author_id.append(row[6])
                time.append(row[27])
                if hide_id is None:
                    reg_text = 'https:\/\/www.google.com\/maps\/reviews\/data=!4m\d+!14m\d+!1m\d+!1m\d+!1s\d+!2s0x\d+:0x(.+)\?hl=.*'
                    hide_id = re.search(reg_text, row[18]).group(1)

            if len(reviews_data) < item_per_page:
                break
        except Exception as e:
            print(response.text.encode('utf8')[:200])
            raise e

    return ({
        'review_id': review_id,
        'rating': rating,
        'time': time,
        'text': text,
        'author_name': author_name,
        'author_id': author_id
    }, hide_id)


def query_poi_info(hide_id):
    url = f'https://www.google.com.tw/maps/preview/place?authuser=0&hl=zh-TW&gl=tw&pb=!1m13!1s0x{0}%3A0x{hide_id}!3m8!1m3!1d283106.8232524803!2d120.8354982!3d24.8010792!3m2!1i798!2i938!4f13.1!4m2!3d24.8035924!4d120.9837826!12m4!2m3!1i360!2i120!4i8!13m57!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240!7m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!9b0!14m2!1s9o_bXuOpIqGHr7wP9OOC4AI!7e81!15m46!1m12!13m6!2b1!3b1!4b1!6i1!8b1!9b1!18m4!3b1!4b1!5b1!6b1!2b1!5m5!2b1!3b1!5b1!6b1!7b1!10m1!8e3!14m1!3b1!17b1!20m2!1e3!1e6!24b1!25b1!26b1!30m1!2b1!36b1!43b1!52b1!55b1!56m2!1b1!3b1!65m5!3m4!1m3!1m2!1i224!2i298!21m28!1m6!1m2!1i0!2i0!2m2!1i458!2i938!1m6!1m2!1i748!2i0!2m2!1i798!2i938!1m6!1m2!1i0!2i0!2m2!1i798!2i20!1m6!1m2!1i0!2i918!2m2!1i798!2i938!22m1!1e81!30m1!3b1'

    response = requests.request("GET", url, headers=HEADERS)
    # to avoid the first 5 unwanted char
    data = json.loads(response.text.encode('utf8')[4:])

    # pretty(data[6][100])

    poi_info = data[6][100]
    if poi_info is None:
        return {}

    poi_info_all = data[6][100][1]
    poi_dict = {}
    for cat in poi_info_all:
        items = cat[2]
        for item in items:
            index_begin = '/geo/type/establishment_poi/'
            if not item[0].startswith(index_begin):
                continue

            poi_index = item[0][len(index_begin):]

            ignore_set = ('pay_credit_card_types_accepted', 'wi_fi')
            if poi_index in ignore_set:
                poi_bool = True
            else:
                poi_bool = bool(item[2][1][0][0])

            poi_dict[poi_index] = poi_bool
    return poi_dict


def query_place_info_poi_info(hide_id):
    url = f'https://www.google.com.tw/maps/preview/place?authuser=0&hl=zh-TW&gl=tw&pb=!1m13!1s0x{0}%3A0x{hide_id}!3m8!1m3!1d283106.8232524803!2d120.8354982!3d24.8010792!3m2!1i798!2i938!4f13.1!4m2!3d24.8035924!4d120.9837826!12m4!2m3!1i360!2i120!4i8!13m57!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240!7m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!9b0!14m2!1s9o_bXuOpIqGHr7wP9OOC4AI!7e81!15m46!1m12!13m6!2b1!3b1!4b1!6i1!8b1!9b1!18m4!3b1!4b1!5b1!6b1!2b1!5m5!2b1!3b1!5b1!6b1!7b1!10m1!8e3!14m1!3b1!17b1!20m2!1e3!1e6!24b1!25b1!26b1!30m1!2b1!36b1!43b1!52b1!55b1!56m2!1b1!3b1!65m5!3m4!1m3!1m2!1i224!2i298!21m28!1m6!1m2!1i0!2i0!2m2!1i458!2i938!1m6!1m2!1i748!2i0!2m2!1i798!2i938!1m6!1m2!1i0!2i0!2m2!1i798!2i20!1m6!1m2!1i0!2i918!2m2!1i798!2i938!22m1!1e81!30m1!3b1'
    response = requests.request("GET", url, headers=HEADERS)
    # to avoid the first 4 unwanted char
    raw_text = response.text.encode('utf8')[4:]
    data = json.loads(raw_text)
    raw_text = raw_text.decode('unicode-escape')

    # pretty(data)
    try:
        # cid = data[6][4][3][0]
        # cid = re.search('.*ludocid=(.+)#.*', cid).group(1)
        cid = parse_cid(str(raw_text))
        place_id = data[6][78]
        formatted_address = data[6][39]
        name = data[6][11]
        lat = float(data[4][0][2]) if data[4][0][2] else None
        lng = float(data[4][0][1]) if data[4][0][1] else None
        user_ratings_total = int(data[6][4][8]) if data[6][4][8] else None
        price_level = len(data[6][4][2]) if data[6][4][2] else None
        rating = float(data[6][4][7]) if data[6][4][7] else None
        types = [v[0] for v in data[6][76]] if data[6][76] else None
    except Exception as e:
        # print(response.text.encode('utf8').decode('utf8'))[4:500]
        # print('happy!!!!')
        # print(url)
        raise(e)

    place_info_dict = {
        'cid': cid,
        'place_id': place_id,
        'hide_id': hide_id,
        'formatted_address': formatted_address,
        'name': name,
        'lat': lat,
        'lng': lng,
        'user_ratings_total': user_ratings_total,
        'price_level': price_level,
        'rating': rating,
        'types': types
    }

    poi_dict = None
    poi_info = data[6][100]
    if poi_info is not None:
        poi_dict = {}
        poi_dict['cid'] = cid
        poi_info_all = data[6][100][1]
        for cat in poi_info_all:
            items = cat[2]
            for item in items:
                index_begin = '/geo/type/establishment_poi/'
                if not item[0].startswith(index_begin):
                    continue

                poi_index = item[0][len(index_begin):]

                ignore_set = ('pay_credit_card_types_accepted', 'wi_fi',
                              'wheelchair_rental_offerings')
                if poi_index in ignore_set:
                    poi_bool = True
                else:
                    try:
                        poi_bool = bool(item[2][1][0][0])
                    except Exception as e:
                        print(item)
                        raise e

                poi_dict[poi_index] = poi_bool
    return place_info_dict, poi_dict


def query_nearby(location=(25.0465677, 121.5437436), radius=50000, max_query_times=200, type='restaurant'):
    global APIKEY_CALLS
    next_page_token = None
    # keys = ['place_id', 'name', 'rating', 'user_ratings_total']
    place_info_list = []

    for i in range(max_query_times):
        if i == 0:
            # url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={APIKEY}&radius={radius}&location={location[0]},{location[1]}&type={type}&language=zh-TW'
            url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={APIKEY}&rankby=distance&location={location[0]},{location[1]}&type={type}&language=zh-TW'
        else:
            url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={APIKEY}&pagetoken={next_page_token}&language=zh-TW'

        APIKEY_CALLS += 1
        print('apicalls:', APIKEY_CALLS)
        response = requests.request("GET", url, headers=HEADERS)
        data = json.loads(response.text.encode('utf8'))

        next_page_token = data['next_page_token'] if 'next_page_token' in data else None
        results = data['results']

        if len(results) == 0:
            break

        for place_info in results:
            try:
                '''
                assert all(
                    key in place_info for key in keys), ('Some keys lost.', place_info)
                '''
                # pretty(place_info)
                # cid = query_cid_by_place_id(place_info['place_id'])
                # place_info = {key: place_info[key] for key in keys}
                # place_info['cid'] = cid
                place_info_list.append(place_info)
            except:
                # print('some location in wrong format!', place_info['name'])
                pass

        logging.debug(
            f'Successfully queried nearby {location} restaurants page {i}.')
        if next_page_token is None:
            break

    return place_info_list


def parse_cid(raw_text):
    cid = None
    try:
        pattern = re.compile(r'(?<=ludocid=)\d*')
        # print(pattern.findall(raw_text))
        cid = str(pattern.findall(raw_text)[0])
    except:
        try:
            pattern = re.compile(r'(?<=fp=)\d+')
            cid = str(pattern.findall(raw_text)[0])
        except Exception as e:
            # print(raw_text)
            # print(e)
            return
            # raise e
    return cid


def get_cid(data, i):
    cid = None
    try:
        pattern = re.compile(r'(?<=ludocid=)\d*')
        decoded_text = str(data[0][1][i][14][4][3][0]).encode(
            'utf8').decode('unicode-escape')
        c = pattern.findall(decoded_text)[0]
        cid = str(c)
    except:
        try:
            pattern = re.compile(r'(?<=fp=)\d+')
            decoded_text = str(data[0][1][i][14][176][3]).encode(
                'utf8').decode('unicode-escape')
            cid = pattern.findall(decoded_text)[0]
        except Exception as e:
            print(e)
            cid = None
    return cid
    

skip_places_cids = set()
skip_places_names = set()


def query_nearby2(location=(22.0108477, 120.7440363), query_per_time=500, type='餐廳'):
    lng, lat = location
    place_info_list = []
    for i in range(1):
        # url = f'https://www.google.com/search?tbm=map&authuser=0&hl=zh-TW&gl=tw&pb=!4m12!1m3!1d300.0!2d{lat}!3d{lng}!2m3!1f0!2f0!3f0!3m2!1i1573!2i1215!4f13.1!7i{query_per_time}!8i{query_per_time * i}!10b1!{"14b1!"}12m8!1m1!18b1!2m3!5m1!6e2!20e3!10b1!16b1!19m4!2m3!1i360!2i120!4i8!20m57!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240!7m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!9b0!22m2!1sKXcxX8DYH5eS0gS5y6OwDw!7e81!24m50!1m12!13m6!2b1!3b1!4b1!6i1!8b1!9b1!18m4!3b1!4b1!5b1!6b1!2b1!5m5!2b1!3b1!5b1!6b1!7b1!10m1!8e3!14m1!3b1!17b1!20m4!1e3!1e6!1e14!1e15!21e2!24b1!25b1!26b1!29b1!30m1!2b1!36b1!43b1!52b1!55b1!56m2!1b1!3b1!65m5!3m4!1m3!1m2!1i224!2i298!26m4!2m3!1i80!2i92!4i8!30m28!1m6!1m2!1i0!2i0!2m2!1i458!2i1215!1m6!1m2!1i1523!2i0!2m2!1i1573!2i1215!1m6!1m2!1i0!2i0!2m2!1i1573!2i20!1m6!1m2!1i0!2i1195!2m2!1i1573!2i1215!34m14!2b1!3b1!4b1!6b1!8m4!1b1!3b1!4b1!6b1!9b1!12b1!14b1!20b1!23b1!37m1!1e81!42b1!47m0!49m1!3b1!50m4!2e2!3m2!1b1!3b1!65m0&q=%E9%A4%90%E5%BB%B3'
        url = f'https://www.google.com/search?tbm=map&authuser=0&hl=zh-TW&gl=tw&pb=!4m12!1m3!1d300.0!2d{lat}!3d{lng}!2m3!1f0!2f0!3f0!3m2!1i1573!2i1215!4f13.1!7i{query_per_time}!8i{query_per_time * i}!10b1!{"14b1!"}12m8!1m1!18b1!2m3!5m1!6e2!20e3!10b1!16b1!19m4!2m3!1i360!2i120!4i8!20m57!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240!7m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!9b0!22m2!1sKXcxX8DYH5eS0gS5y6OwDw!7e81!24m50!1m12!13m6!2b1!3b1!4b1!6i1!8b1!9b1!18m4!3b1!4b1!5b1!6b1!2b1!5m5!2b1!3b1!5b1!6b1!7b1!10m1!8e3!14m1!3b1!17b1!20m4!1e3!1e6!1e14!1e15!21e2!24b1!25b1!26b1!29b1!30m1!2b1!36b1!43b1!52b1!55b1!56m2!1b1!3b1!65m5!3m4!1m3!1m2!1i224!2i298!26m4!2m3!1i80!2i92!4i8!30m28!1m6!1m2!1i0!2i0!2m2!1i458!2i1215!1m6!1m2!1i1523!2i0!2m2!1i1573!2i1215!1m6!1m2!1i0!2i0!2m2!1i1573!2i20!1m6!1m2!1i0!2i1195!2m2!1i1573!2i1215!34m14!2b1!3b1!4b1!6b1!8m4!1b1!3b1!4b1!6b1!9b1!12b1!14b1!20b1!23b1!37m1!1e81!42b1!47m0!49m1!3b1!50m4!2e2!3m2!1b1!3b1!65m0&q={type}'
        # &tch=1&ech=1&psi=KXcxX8DYH5eS0gS5y6OwDw.1597077291767.1
        
        response = requests.request("GET", url, headers=HEADERS)
        raw_text = response.text.encode('utf8')[4:]
        data = json.loads(raw_text)
        # raw_text = raw_text.decode('unicode-escape')
        # pretty(data)

        for i in range(1, len(data[0][1])):
            try:
                name = str(data[0][1][i][14][11])
                lat = str(data[0][1][i][14][9][2])
                lng = str(data[0][1][i][14][9][3])
                place_id = str(data[0][1][i][14][78])
                formatted_address = None
                cid = None
                
                try:
                    if formatted_address is None:
                        formatted_address = str(data[0][1][i][14][2][0])
                except:
                    pass
                
                try:
                    if cid is None:
                        cid = str(data[0][1][i][14][37][0][0][29][1])
                except:
                    pass
                
                try:
                    if cid is None:
                        cid = str(data[0][1][i][14][52][0][0][31][1])
                except:
                    pass
                
                try:
                    if cid is None:
                        ox = data[0][1][i][14][10].split(':')[1]
                        cid = int(ox, 16)
                except:
                    pass
                
                try:
                    if cid is None:
                        cid = parse_cid(str(data[0][1][i]))
                except:
                    pass
                
                if cid is None:
                    raise Exception('missing cid')
                
                if cid is not None and int(cid) < 0:
                    cid = int(cid) + 2 ** 64
            
                item = {
                    'place_id': place_id,
                    'cid': cid,
                    'name': name,
                    'lat': lat,
                    'lng': lng,
                    'formatted_address': formatted_address
                }
    
                place_info_list.append(item)
            except:
                print(item)
                print(url)
                f = open(f'./sad.{name}.json', 'w', encoding='utf-8')
                f.write(json.dumps(data[0][1][i]))
                f.close()
                print(name, place_id)
                raise Exception('fuck')
    return place_info_list
