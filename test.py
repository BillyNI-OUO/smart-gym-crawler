import logging
import requests
import json
import re

APIKEY = 'AIzaSyAie5EFbKi2Wfg0C0DPiRAthPD2gTD5_9s'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

def query_nearby2(location=(22.0108477, 120.7440363), query_per_time=500, type='餐廳'):
    lng, lat = location
    place_info_list = []
    for i in range(1):
        # url = f'https://www.google.com/search?tbm=map&authuser=0&hl=zh-TW&gl=tw&pb=!4m12!1m3!1d300.0!2d{lat}!3d{lng}!2m3!1f0!2f0!3f0!3m2!1i1573!2i1215!4f13.1!7i{query_per_time}!8i{query_per_time * i}!10b1!{"14b1!"}12m8!1m1!18b1!2m3!5m1!6e2!20e3!10b1!16b1!19m4!2m3!1i360!2i120!4i8!20m57!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240!7m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!9b0!22m2!1sKXcxX8DYH5eS0gS5y6OwDw!7e81!24m50!1m12!13m6!2b1!3b1!4b1!6i1!8b1!9b1!18m4!3b1!4b1!5b1!6b1!2b1!5m5!2b1!3b1!5b1!6b1!7b1!10m1!8e3!14m1!3b1!17b1!20m4!1e3!1e6!1e14!1e15!21e2!24b1!25b1!26b1!29b1!30m1!2b1!36b1!43b1!52b1!55b1!56m2!1b1!3b1!65m5!3m4!1m3!1m2!1i224!2i298!26m4!2m3!1i80!2i92!4i8!30m28!1m6!1m2!1i0!2i0!2m2!1i458!2i1215!1m6!1m2!1i1523!2i0!2m2!1i1573!2i1215!1m6!1m2!1i0!2i0!2m2!1i1573!2i20!1m6!1m2!1i0!2i1195!2m2!1i1573!2i1215!34m14!2b1!3b1!4b1!6b1!8m4!1b1!3b1!4b1!6b1!9b1!12b1!14b1!20b1!23b1!37m1!1e81!42b1!47m0!49m1!3b1!50m4!2e2!3m2!1b1!3b1!65m0&q=%E9%A4%90%E5%BB%B3'
        url = f'https://www.google.com/search?tbm=map&authuser=0&hl=zh-TW&gl=zh-TW&pb=!4m12!1m3!1d300.0!2d{lat}!3d{lng}!2m3!1f0!2f0!3f0!3m2!1i1573!2i1215!4f13.1!7i{15}!10b1!14b1!12m8!1m1!18b1!2m3!5m1!6e2!20e3!10b1!16b1!19m4!2m3!1i360!2i120!4i8!20m57!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240!7m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!9b0!22m2!1sKXcxX8DYH5eS0gS5y6OwDw!7e81!24m50!1m12!13m6!2b1!3b1!4b1!6i1!8b1!9b1!18m4!3b1!4b1!5b1!6b1!2b1!5m5!2b1!3b1!5b1!6b1!7b1!10m1!8e3!14m1!3b1!17b1!20m4!1e3!1e6!1e14!1e15!21e2!24b1!25b1!26b1!29b1!30m1!2b1!36b1!43b1!52b1!55b1!56m2!1b1!3b1!65m5!3m4!1m3!1m2!1i224!2i298!26m4!2m3!1i80!2i92!4i8!30m28!1m6!1m2!1i0!2i0!2m2!1i458!2i1215!1m6!1m2!1i1523!2i0!2m2!1i1573!2i1215!1m6!1m2!1i0!2i0!2m2!1i1573!2i20!1m6!1m2!1i0!2i1195!2m2!1i1573!2i1215!34m14!2b1!3b1!4b1!6b1!8m4!1b1!3b1!4b1!6b1!9b1!12b1!14b1!20b1!23b1!37m1!1e81!42b1!47m0!49m1!3b1!50m4!2e2!3m2!1b1!3b1!65m0&q=餐廳'
        # &tch=1&ech=1&psi=KXcxX8DYH5eS0gS5y6OwDw.1597077291767.1
        print(url)
        response = requests.request("GET", url, headers=HEADERS)
        raw_text = response.text.encode('utf8')[4:]
        data = json.loads(raw_text)
        # raw_text = raw_text.decode('unicode-escape')
        # pretty(data)

        for i in range(1, 10):
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
                    'formatted_address': formatted_address}
                print(item)
                #place_info_list.append(item)
            except:
                print(item)
                print(url)
                f = open(f'./sad.{name}.json', 'w', encoding='utf-8')
                f.write(json.dumps(data[0][1][i]))
                f.close()
                print(name, place_id)
                raise Exception('fuck')
    #return place_info_list

query_nearby2()