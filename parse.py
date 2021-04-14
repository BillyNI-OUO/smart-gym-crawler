# -*- coding: utf-8 -*-

from data import auto_download_step2, grid_search, grid_search2 ,con
import sys
import re

method = 'low'
filepath = './coordinates/台中.txt'
from_index = 0

if len(sys.argv) > 1:
    if sys.argv[1] != '-f':
        method = str(sys.argv[1])

        if len(sys.argv) > 2:
            if method in ['high', 'low']:
                filepath = str(sys.argv[2])
            elif method == 'again':
                from_index = int(sys.argv[2])
    print("!!")

if method in ['high', 'low']:
    print('Load coordinates file from:', filepath)

    def open_coordinates_file(filepath):
        if not isinstance(filepath, str):
            raise Exception('File path must be provided.')

        stores_list_file = open(filepath, 'r', encoding="utf-8")
        lines = stores_list_file.read().splitlines()

        cor_list = []
        lines = filter(lambda v: len(v) > 0, lines)
        in_comment = False
        for line in lines:
            if line == '<!--':
                in_comment = True
            elif line == '-->':
                in_comment = False
                continue
            if in_comment:
                continue
            
            s = re.split('[,|\s|\t]+', line)
            s = list(map(float, s))
            cor = ((s[0], s[1]), (s[2], s[3]))
            cor_list.append(cor)

        return cor_list

    cors = open_coordinates_file(filepath)


    for sw, ne in cors:
        lat_range = (min(sw[0], ne[0]), max(sw[0], ne[0]))
        lng_range = (min(sw[1], ne[1]), max(sw[1], ne[1]))
        
        print('=========== NEW PLACE ============')
        print(lat_range, lng_range)

        if method == 'high':
            grid_search(type='restaurant',
                        lat_range=lat_range, lng_range=lng_range)
        elif method == 'low':
            grid_search2(type='餐廳',
                    lat_range=lat_range, lng_range=lng_range)

elif method == 'again':
    print('Again from:', from_index)

    try:
        start = from_index
        limit = 20000
        sql = f'''
        SELECT * FROM `place_info`
        WHERE `id` >= {start} ORDER BY `id` LIMIT {limit};
        '''
        cur = con.cursor(dictionary=True, buffered=True)
        cur.execute(sql)
        i = 0
        while True:
            place = cur.fetchone()
            if place is None:
                break
            print(start + i, ' ', end='')
            i += 1
            
            lat = place['lat']
            lng = place['lng']
            if ((21.82089 <= lat <= 25.40368) and (119.88978 <= lng <= 122.41664)) or \
               ((23.01713 <= lat <= 23.88613) and (119.21612 <= lng <= 119.89857)) or \
               ((24.35004 <= lat <= 24.52757) and (118.21111 <= lng <= 118.51255)) or \
               ((25.8827 <= lat <= 26.29837) and (119.8965 <= lng <= 120.08647)) or \
               ((26.24541 <= lat <= 26.43002) and (120.33321 <= lng <= 120.66417)):
                auto_download_step2((place['lat'], place['lng']))
        con.commit()
        cur.close()
        con.close()
    except Exception as e:
        print('sad', e)
        con.close()
        raise e


