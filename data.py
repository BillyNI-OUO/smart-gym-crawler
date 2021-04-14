# -*- coding: utf-8 -*-
import pandas as pd
import re
import numpy as np
import crawler
import copy
import logging
import time
import itertools
import sys
import mysql.connector
import datetime


handler1 = logging.FileHandler('crawler.log', 'a', 'utf-8')
handler2 = logging.StreamHandler(stream=sys.stdout)
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s][%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[handler1, handler2])

logging.info('Initialized data module.')


con = mysql.connector.connect(
    host='120.126.17.206',        # 主機名稱
    database='smart_restaurant',  # 資料庫名稱
    user='smartuser',            # 帳號
    password='pp253&$@')  # 密碼


def init_db():
    """
    some sql create statements...
    """

    c = con.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS "place_info" (
                 "id"	TEXT UNIQUE,
                 "place_id"	TEXT NOT NULL UNIQUE,
                 "cid"	TEXT NOT NULL UNIQUE,
                 "hide_id"	TEXT UNIQUE,
                 "name"	TEXT NOT NULL,
                 "lat" TEXT,
                 "lng" TEXT,
                 "formatted_address"	TEXT,
                 "user_ratings_total" INTEGER,
                 "price_level" TEXT,
                 "rating" REAL,
                 "types" TEXT,
                 PRIMARY KEY("id","place_id","cid","hide_id")
                 )""")
    con.commit()

    c.execute("""CREATE TABLE IF NOT EXISTS "poi_info" (
                 "cid" TEXT,
                 "has_takeout" TEXT,
                 "has_wheelchair_accessible_entrance" REAL,
                 "has_wheelchair_accessible_restroom" REAL,
                 "has_wheelchair_accessible_seating" TEXT,
                 "has_wheelchair_accessible_parking" TEXT,
                 "serves_organic" TEXT,
                 "has_childrens_menu" TEXT,
                 "serves_late_night_food" TEXT,
                 "serves_vegetarian" TEXT,
                 "welcomes_children" REAL,
                 "feels_casual" REAL,
                 "feels_cozy" REAL,
                 "suitable_for_groups" REAL,
                 "pay_mobile_nfc" REAL,
                 "has_delivery" REAL,
                 "pay_credit_card_types_accepted" REAL,
                 "has_restroom" REAL,
                 "wi_fi" TEXT,
                 "has_high_chairs" TEXT,
                 "serves_lunch" REAL,
                 "has_all_you_can_eat_always" REAL,
                 "pay_debit_card" TEXT,
                 "welcomes_families" REAL,
                 "has_salad_bar" REAL,
                 "has_wheelchair_accessible_elevator" REAL,
                 "serves_beer" REAL,
                 "serves_dessert" REAL,
                 "serves_dinner" REAL,
                 "requires_cash_only" REAL,
                 "suitable_for_watching_sports" REAL,
                 "has_catering" REAL,
                 "has_seating" REAL,
                 "serves_dine_in" REAL,
                 "serves_cocktails_notable" REAL,
                 "serves_wine" REAL,
                 "has_live_music" REAL,
                 "requires_reservations" REAL,
                 "serves_breakfast" REAL,
                 "is_owned_by_women" REAL,
                 "welcomes_lgbtq" REAL,
                 "has_seating_outdoors" REAL,
                 "has_fireplace" REAL,
                 "has_restaurant" REAL,
                 "has_bar_onsite" REAL,
                 "serves_happy_hour_food" REAL,
                 "serves_halal_food" REAL,
                 "has_seating_rooftop" REAL,
                 "is_smoke_free_property" REAL,
                 "pay_check" REAL,
                 "has_restroom_public" REAL
                 )""")
    con.commit()

    c.execute("""CREATE TABLE IF NOT EXISTS "reviews" (
                 "cid"	TEXT NOT NULL,
                 "rating"	INTEGER,
                 "time"	INTEGER,
                 "text"	TEXT,
                 "author_name"	TEXT,
                 "author_id"	TEXT,
                 "review_id"	TEXT NOT NULL,
                 PRIMARY KEY("review_id","cid")
                 )""")
    con.commit()

    c.execute("""CREATE INDEX IF NOT EXISTS "reviews_index" ON "reviews" (
                 "cid" ASC
                 )""")

    logging.info('Create database successfully.')
    return True


def is_place_info_exists(cid):
    sql = f'SELECT `place_id` FROM `place_info` WHERE `cid`="{cid}";'
    cur = con.cursor()
    cur.execute(sql)
    result = cur.fetchone()
    cur.close()
    if result == None:
        return False
    else:
        return True


def is_place_info_exists_by_place_id(place_id):
    sql = f'SELECT `place_id` FROM `place_info` WHERE `place_id`="{place_id}";'
    cur = con.cursor()
    cur.execute(sql)
    result = cur.fetchone()
    cur.close()
    if result == None:
        return False
    else:
        return True


def cid2place_id(cid):
    sql = f'SELECT `place_id` FROM `place_info` WHERE `cid`="{cid}";'
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    place_id = cur.fetchone()['place_id']
    cur.close()
    return place_id


def place_id2cid(place_id):
    sql = f'SELECT `cid` FROM `place_info` WHERE `place_id`="{place_id}";'
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    place_id = cur.fetchone()['cid']
    cur.close()
    return place_id


def cid2hide_id(cid):
    sql = f'SELECT `hide_id` FROM `place_info` WHERE `cid`="{cid}";'
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    hide_id = cur.fetchone()['hide_id']
    cur.close()
    return hide_id


def review_id2cid(review_id):
    sql = f'SELECT `cid` FROM `reviews` WHERE `review_id`="{review_id}";'
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    cid = cur.fetchone()['cid']
    cur.close()
    return cid


def query_poi_info(cid):
    sql = f'SELECT * FROM `poi_info` WHERE `cid`="{cid}";'
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    poi_info = cur.fetchone()
    return poi_info


def query_place_info_iter():
    sql = 'SELECT * FROM `place_info`;'
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    while True:
        place_info = cur.fetchone()
        if place_info is None:
            break
        yield place_info


def query_reviews_iter():
    sql = 'SELECT * FROM `reviews`;'
    cur = con.cursor(dictionary=True)
    cur.execute(sql)

    while True:
        review = cur.fetchone()
        if review is None:
            cur.close()
            break
        yield review


def save_place_info(place_info):
    assert 'cid' in place_info, 'Missing `cid`.'
    place_info = copy.deepcopy(place_info)
    cid = place_info['cid']
    if 'types' in place_info and place_info['types']:
        place_info['types'] = ','.join(place_info['types'])

    last_update = datetime.datetime.fromtimestamp(time.time()).astimezone(
        datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    sql = '''
    INSERT INTO `place_info`
    (place_id, cid, hide_id, name, lat, lng, formatted_address,
     user_ratings_total, price_level, rating, types)
    VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    place_id=%s, hide_id=%s, name=%s, lat=%s, lng=%s, formatted_address=%s,
    user_ratings_total=%s, price_level=%s, rating=%s, types=%s, last_update=%s;
    '''
    cur = con.cursor()
    cur.execute(sql, (
        place_info['place_id'],
        place_info['cid'],
        place_info.get('hide_id', None),
        place_info.get('name', None),
        place_info.get('lat', None),
        place_info.get('lng', None),
        place_info.get('formatted_address', None),
        place_info.get('user_ratings_total', None),
        place_info.get('price_level', None),
        place_info.get('rating', None),
        place_info.get('types', None),

        place_info['place_id'],
        place_info.get('hide_id', None),
        place_info.get('name', None),
        place_info.get('lat', None),
        place_info.get('lng', None),
        place_info.get('formatted_address', None),
        place_info.get('user_ratings_total', None),
        place_info.get('price_level', None),
        place_info.get('rating', None),
        place_info.get('types', None),
        last_update
    ))

    con.commit()
    cur.close()

    logging.debug(
        f'Save new place info {place_info["name"]} (cid: {cid}) to db.')
    return place_info


def download_place_info(query_text):
    place_info = crawler.query_place_info(query_text)
    cid = crawler.query_cid_by_place_id(place_info['place_id'])
    place_info['cid'] = cid

    save_place_info(place_info)
    return place_info


def set_hide_id(cid, hide_id):
    sql = f'UPDATE `place_info` SET `hide_id`="{hide_id}" WHERE `cid`="{cid}";'
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    cur.close()


def download_reviews(cid, max_query_times=100, iter_per_page=199):
    reviews, hide_id = crawler.query_reviews(
        cid, max_query_times, iter_per_page)
    set_hide_id(cid, hide_id)

    cur = con.cursor()
    cur.execute(f'DELETE FROM `reviews` WHERE `cid`="{cid}";')
    con.commit()

    sql = '''
    INSERT INTO `reviews`
    (cid, rating, time, text, author_name, author_id, review_id)
    VALUES
    (%s, %s, %s, %s, %s, %s, %s);
    '''

    def generator():
        for i in range(len(reviews['review_id'])):
            time = reviews['time'][i] // 1000
            dt = datetime.datetime.fromtimestamp(time).astimezone(
                datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            yield (
                cid,
                reviews['rating'][i],
                dt,
                reviews['text'][i],
                reviews['author_name'][i],
                reviews['author_id'][i],
                reviews['review_id'][i]
            )
    cur.executemany(sql, list(generator()))
    con.commit()
    cur.close()

    logging.debug(f'Save new reviews cid: {cid} to db.')
    return (reviews, hide_id)


def split_review_text_iter(review_text):
    for line in review_text.splitlines():
        stripped_line = line.strip()
        if len(stripped_line) == 0:
            continue

        for sep_line in re.split('。|，|；|﹐|！|\!|,|\?|？|；|;|\t', stripped_line):
            sep_line = sep_line.strip()
            if len(sep_line) > 20 or len(sep_line) <= 2:
                continue
            yield sep_line


def reviews_sep_lines_iter():
    for review in query_reviews_iter():
        text = review['text']
        if text is None or text.startswith('(由 Google 提供翻譯)'):
            continue

        sep_lines = list(split_review_text_iter(text))

        return_review_dict = review.copy()
        return_review_dict['sep_lines'] = sep_lines
        yield return_review_dict


def make_reviews_sep_lines_file(file='data/reviews_sep_lines.tsv'):
    f = open(file, "w", encoding="utf-8")
    line_count = 0
    for review in reviews_sep_lines_iter():
        for sep_line in review['sep_lines']:
            f.write(
                f'{review["rating"]}\t{sep_line}\t{review["cid"]}\t{review["time"]}\t{review["author_name"]}\t{review["author_id"]}\t{review["review_id"]}\n')
            line_count += 1
    f.close()

    logging.info(
        f'Successfully create a new file ({line_count} lines), {file}.')


def make_place_info_file(file='data/place_info.tsv'):
    f = open(file, "w", encoding="utf-8")
    line_count = 0
    for place_info in query_place_info_iter():
        f.write(
            f'{place_info["id"]}\t{place_info["place_id"]}\t{place_info["cid"]}\t{place_info["hide_id"]}\t{place_info["name"]}\t{place_info["formatted_address"]}\t{place_info["user_ratings_total"]}\t{place_info["price_level"]}\t{place_info["rating"]}\t\n')
        line_count += 1
    f.close()

    logging.info(
        f'Successfully create a new file ({line_count} lines), {file}.')


def get_place_info_df():
    df = pd.read_sql('SELECT * FROM `place_info`;', con=con)
    return df


def get_reviews_df():
    df = pd.read_sql('SELECT * FROM `place_info`;', con=con)
    return df


def get_place_reviews_df(cid):
    df = pd.read_sql(f"SELECT * FROM `reviews` WHERE `cid`='{cid}';", con=con)
    return df


def get_place_poi_info_df(cid):
    df = pd.read_sql(f"SELECT * FROM `poi_info` WHERE `cid`='{cid}';", con=con)
    return df


def download_poi_info(cid):
    hide_id = cid2hide_id(cid)
    poi_info = crawler.query_poi_info(hide_id)

    cur = con.cursor()
    cur.execute(f'DELETE FROM `poi_info` WHERE `cid`="{cid}";')
    cur.close()

    poi_info['cid'] = cid
    df = pd.DataFrame()
    df = df.append(poi_info, ignore_index=True)

    try:
        # this will fail if there is a new column
        df.to_sql(name='poi_info', con=con, if_exists='append', index=False)
    except:
        data = pd.read_sql('SELECT * FROM `poi_info`;', con)
        df2 = pd.concat([data, df])
        df2.to_sql(name='poi_info', con=con, if_exists='replace', index=False)

    con.commit()

    logging.debug(f'Save new poi info cid: {cid} to db.')
    return poi_info


def save_poi_info(poi_info):
    if 'cid' not in poi_info:
        raise Exception('cid cannnot be empty in poi_info.')

    cid = poi_info['cid']
    cur = con.cursor()
    new_cols = list(set(poi_info.keys()) - set(('cid', 'id')))

    try:
        # this will fail if there is a new column
        sql = 'INSERT INTO `poi_info` (cid, ' + ','.join(new_cols) +\
            ') VALUES (' + ','.join(['%s'] * (len(new_cols) + 1)) +\
            ') ON DUPLICATE KEY UPDATE ' +\
            ','.join(col + '=%s' for col in new_cols) + ';'
        args = [poi_info['cid']] + [poi_info[col] for col in new_cols] * 2
        cur.execute(sql, args)
    except:
        # get all columns
        cur.execute("SHOW columns FROM `poi_info`;")
        old_cols = set(column[0] for column in cur.fetchall())
        diff_cols = set(new_cols) - old_cols
        
        for col in diff_cols:
            sql = '''
            ALTER TABLE `poi_info` ADD %s BOOLEAN NOT NULL DEFAULT FALSE AFTER `last_update`;
            '''
            cur.execute(sql, (col,))
        con.commit()
        
        # this will fail if there is a new column
        args = [poi_info['cid']] + [poi_info[col] for col in new_cols] * 2
        cur.execute('INSERT INTO `poi_info` (cid, ' + ','.join(new_cols) +
                    ') VALUES (' + ','.join(['%s'] * len(new_cols)) +
                    ') ON DUPLICATE KEY UPDATE ' +
                    ','.join(col + '=%s' for col in new_cols) + ';',
                    args)

    cur.close()
    con.commit()

    logging.debug(f'Save new poi info cid: {cid} to db.')


def download_place(query_text):
    place_info = download_place_info(query_text)
    cid = place_info['cid']
    download_reviews(cid, max_query_times=200, iter_per_page=199)
    # download_poi_info(cid)


def download_by_place_info_list(place_info_list, force_update=False):
    filtered_place_info_list = []
    for place_info in place_info_list:
        try:
            start = time.time()
            
            cid = None
            if 'cid' in place_info:
                cid = place_info['cid']
            else:
                place_id = place_info['place_id']
                if is_place_info_exists_by_place_id(place_id):
                    cid = place_id2cid(place_id)
                else:
                    # print(f'[WARNING] missing cid and update: {place_id}')
                    cid = crawler.query_cid_by_place_id(place_id)

            if force_update == False and is_place_info_exists(cid):
                continue
            if force_update == False and is_place_info_exists_by_place_id(place_info['place_id']):
                logging.warning(
                    f'Duplicated place_info: {place_info["name"]} (place_id={place_info["place_id"]}).')
                logging.debug(f'Save new poi info cid: {cid} to db.')
                continue
            
            reviews_num = 0
            place_info['cid'] = cid
            
            if 'user_ratings_total' not in place_info or place_info['user_ratings_total'] == 0:
                place_info['lat'] = place_info['geometry']['location']['lat']
                place_info['lng'] = place_info['geometry']['location']['lng']
                place_info['formatted_location'] = place_info.get('vicinity', None)
                save_place_info(place_info)
                filtered_place_info_list.append(place_info)
            else:
                reviews, hide_id = download_reviews(
                    cid, max_query_times=500, iter_per_page=199)
    
                detailed_place_info, poi_info = crawler.query_place_info_poi_info(
                    hide_id)
                detailed_place_info['cid'] = cid
                if 'types' in place_info:
                    detailed_place_info['types'] = place_info['types']
                
    
                save_place_info(detailed_place_info)
                filtered_place_info_list.append(detailed_place_info)
    
                if poi_info is not None:
                    poi_info['cid'] = cid
                    save_poi_info(poi_info)
    
                reviews_num = len(reviews['review_id'])
                diff_reviews_num = abs(
                    reviews_num - detailed_place_info['user_ratings_total'])
                if diff_reviews_num > 100:
                    logging.warning(
                        f'{detailed_place_info["name"]}(cid={detailed_place_info["cid"]}')
                del reviews
                del hide_id

            time_length = time.time() - start
            logging.info(
                f'Auto download succesfully: {place_info["name"]}(cid={place_info["cid"]}, reviews_num={reviews_num}, time_length={time_length:.2f})')
        except mysql.connector.Error as e:
            print(e)
            raise e
        except Exception as e:
            logging.warning('download_by_place_info_list failed!')
            if 'name' in place_info:
                logging.warning(place_info['name'])
            # crawler.pretty(place_info)
            
            print(e)
            # raise e
    return filtered_place_info_list


def auto_download_stores(query_text_list, type='restaurant', force_update=False):
    for query_text in query_text_list:
        place_info = crawler.query_place_info(query_text, type)
        filtered_place_info_list = download_by_place_info_list(
            [place_info], force_update)
        logging.info(
            f'Auto download store {query_text} successfully.')


def auto_download_chainstores(query_text_list, max_query_times=200,
                              type='restaurant', force_update=False):
    for query_text in query_text_list:
        place_info_list = crawler.query_multiple_place_info(
            query_text, max_query_times, type)
        filtered_place_info_list = download_by_place_info_list(
            place_info_list, force_update)
        logging.info(
            f'Auto download chainstore {query_text}: {len(filtered_place_info_list)} stores updated.')


def auto_download_step(location, radius=150, max_query_times=200, force_update=False, type='restaurant'):
    place_info_list = crawler.query_nearby(
        location, radius, max_query_times, type)
    filtered_place_info_list = download_by_place_info_list(
        place_info_list, force_update)
    return filtered_place_info_list


def auto_download(initial_location=(23.9866451, 121.5909399),
                  max_query_times=10, force_update=False,
                  type='restaurant', visited_locs=None):
    if visited_locs is None:
        visited_locs = set()
    queued_locs = set()
    queued_locs.add(initial_location)

    for i in range(max_query_times):
        next_locs = set()
        for location in queued_locs:
            place_info_list = auto_download_step(
                location, radius=100, force_update=force_update, type=type)
            next_locs |= set(
                map(lambda v: (v['lat'], v['lng']), place_info_list))
            '''
            try:
                pass
            except Exception as e:
                print(e)
            '''

        visited_locs |= queued_locs
        queued_locs = next_locs - visited_locs

        logging.info(
            f'Successfully automated download nearby {type} iteration {i}. (next queued_locs={len(queued_locs)})')

        if len(queued_locs) == 0:
            break
    return visited_locs


skip_places_cids = set()


def download_by_place_info_list2(place_info_list, force_update=False):
    filtered_place_info_list = []
    for place_info in place_info_list:
        try:
            cid = None
            if 'cid' in place_info:
                cid = place_info['cid']
            else:
                place_id = place_info['place_id']
                if is_place_info_exists_by_place_id(place_id):
                    cid = place_id2cid(place_id)
                else:
                    print(f'[WARNING] missing cid and update: {place_id}')
                    raise Exception(
                        f'[WARNING] missing cid and update: {place_id}')

            if force_update == False and is_place_info_exists(cid):
                continue
            if force_update == False and is_place_info_exists_by_place_id(place_info['place_id']):
                print(place_info)
                logging.warning(
                    f'Duplicated place_info: {place_info["name"]} (place_id={place_info["place_id"]}).')
                logging.debug(f'Save new poi info cid: {cid} to db.')
                continue

            start = time.time()

            reviews, hide_id = download_reviews(
                cid, max_query_times=500, iter_per_page=199)
            reviews_num = 0
            
            try:
                detailed_place_info, poi_info = crawler.query_place_info_poi_info(
                    hide_id)
    
                save_place_info(detailed_place_info)
                filtered_place_info_list.append(detailed_place_info)
    
                if poi_info is not None:
                    save_poi_info(poi_info)
    
                reviews_num = len(reviews['review_id'])
                diff_reviews_num = abs(
                    reviews_num - detailed_place_info['user_ratings_total'])
                if diff_reviews_num > 100:
                    logging.warning(
                        f'{detailed_place_info["name"]}(cid={detailed_place_info["cid"]}) diff_reviews_num={diff_reviews_num} too large!')
            except:
                save_place_info(place_info)
                
            
            time_length = time.time() - start
            logging.info(
                f'Auto download succesfully: {place_info["name"]}(cid={place_info["cid"]}, reviews_num={reviews_num}, time_length={time_length:.2f})')

            del reviews
            del hide_id
        except Exception as e:
            if place_info['cid'] not in skip_places_cids:
                logging.warning('download_by_place_info_list failed!')
                if 'name' in place_info:
                    logging.warning(place_info['name'])
                skip_places_cids.add(place_info['cid'])
            # crawler.pretty(place_info)
            print(e)
            # raise e

    return filtered_place_info_list


def auto_download_step2(location, radius=50000, max_query_times=200, force_update=False, type='餐廳'):
    place_info_list = crawler.query_nearby2(
        location, max_query_times, type)
    filtered_place_info_list = download_by_place_info_list2(
        place_info_list, force_update)
    return filtered_place_info_list


def grid_search2(type='餐廳', lat_range=(21.8, 25.44), lng_range=(120, 122)):
    width = np.array((0.0015, 0.0015))
    min_width = width / 2**3

    def _grid_search(anchor, width, _level=0):
        if any(width <= min_width):
            print('!!!! too small', width, min_width)
            return
        center = anchor + width / 2
        nearby_place_info_list = auto_download_step2(center, type=type)

        print('  ' * _level, anchor, width, len(nearby_place_info_list))

        if len(nearby_place_info_list) > 5 and \
            all(anchor[0] <= p['lat'] <= anchor[0] + width[0] and
                anchor[1] <= p['lng'] <= anchor[1] +
                width[1]
                for p in nearby_place_info_list):
            print('  ' * _level + '<===')
            for offset in itertools.product((0, 1), repeat=2):
                new_anchor = anchor + width / 2 * offset
                new_width = width / 2
                _grid_search(new_anchor, new_width, _level=_level + 1)
            print('  ' * _level + '>===')

    for lat in np.arange(lat_range[0], lat_range[1], width[0]):
        for lng in np.arange(lng_range[0], lng_range[1], width[1]):
            anchor = np.array((lat, lng))
            _grid_search(anchor, width)


def grid_search(type='restaurant', lat_range=(21.8, 25.44), lng_range=(120, 122)):
    width = np.array((0.0015, 0.0015))
    min_width = width / 2**3
    
    f = open('locations.log', 'a', encoding='utf-8')

    def _grid_search(anchor, width, _level=0):
        if any(width <= min_width):
            print('!!!! too small', width, min_width)
            return
        center = anchor + width / 2
        nearby_place_info_list = auto_download_step(center, type=type)
        # nearby_place_info_list = [{'lat': 22.3254, 'lng': 121.5445}]

        print('  ' * _level, anchor, width, len(nearby_place_info_list))
        f.write(f'{anchor[0]}, {anchor[1]}\n')
        f.flush()

        if len(nearby_place_info_list) > 5 and \
            all(anchor[0] <= p['lat'] <= anchor[0] + width[0] and
                anchor[1] <= p['lng'] <= anchor[1] + width[1]
                for p in nearby_place_info_list):
            print('  ' * _level + '<===')
            for offset in itertools.product((0, 1), repeat=2):
                new_anchor = anchor + width / 2 * offset
                new_width = width / 2
                _grid_search(new_anchor, new_width, _level=_level + 1)
            print('  ' * _level + '>===')
            

    # 21.8, 25.44
    # 120, 122
    for lat in np.arange(lat_range[0], lat_range[1], width[0]):
        for lng in np.arange(lng_range[0], lng_range[1], width[1]):
            anchor = np.array((lat, lng))
            _grid_search(anchor, width)
            
    f.close()


def open_stores_list(filepath='stores_list.txt'):
    stores_list_file = open(filepath, 'r', encoding="utf-8")
    lines = stores_list_file.read().splitlines()

    stores_list = []
    lines = filter(lambda v: len(v) > 0, lines)
    in_comment = False
    for query_text in lines:
        if query_text == '<!--':
            in_comment = True
        elif query_text == '-->':
            in_comment = False
            continue
        if in_comment:
            continue
        stores_list.append(query_text)

    return stores_list


def validate():
    # check every stores have reviews unless `user_ratings_total` = 0
    # and warn you when `user_ratings_total` - #reviews > 10% * `user_ratings_total`
    sql = """
          SELECT "B"."cid", "B"."name", "B"."user_ratings_total", "B"."rating", "A"."count"
          FROM "place_info" AS "B" LEFT JOIN
          (SELECT "reviews"."cid", COUNT("reviews"."review_id") AS "count"
           FROM "reviews" GROUP BY "reviews"."cid") AS "A"
          ON "A"."cid" = "B"."cid";
          """

    # check every stores have cid, place_id
    # and warn you when hide_id is null

    return True


if __name__ == "__main__":
    # init_db()

    # make_reviews_sep_lines_file()
    # make_place_info_file()
    # stores_list = open_stores_list('./data/chain_store_list.txt')
    # auto_download_chainstores(stores_list)

    '''
    latitude_range = (25.0219775, 25.0719785)
    longitude_range = (121.5002127, 121.5771619)
    step = 0.005
    for la in np.arange(latitude_range[0], latitude_range[1], step):
        for lo in np.arange(longitude_range[0], longitude_range[1], step):
            auto_download((round(la, 7),
                           round(lo, 7)))
    '''

    # grid_search2(type='咖啡廳')
    
    # 台灣範圍
    '''
    23.01713, 119.21612
    23.88613, 119.89857
    
    24.35004, 118.21111
    24.52757, 118.51255
    
    25.8827, 119.8965
    26.29837, 120.08647
    
    26.24541, 120.33321
    26.43002, 120.66417
    '''
    
    '''
    # 台北市 lat_range=(25.04291, 25.073203), lng_range=(121.504635, 121.568056)
    # 新店 lat_range=(24.95934, 24.98512), lng_range=(121.51605, 121.54526)
    # 東台北  lat_range=(25.02987, 25.08555), lng_range=(121.56876, 121.59407)
    # 大直 lat_range=(25.06841, 25.08537), lng_range=(121.54513, 121.56876)
    # 西南台北 lat_range=(24.98424, 25.06991), lng_range=(121.42624, 121.51363)
    # 西北台北 lat_range=(25.06991, 25.10062), lng_range=(121.45045, 121.51363)
    # 新竹
    ranges = [
        # ((24.7876, 120.9599), (24.80884, 120.99087)),
        # ((24.80895, 120.98302), (24.82542, 120.95289)),
        ((24.79159, 120.99103), (24.80457, 121.00832)),
        # ((24.78052, 121.00793), (24.79579, 121.02286)),
        # ((24.79833, 121.03751), (24.81204, 121.04969)),
        # ((24.84885, 121.02176), (24.81009, 121.00478)),
        # ((24.79833, 121.03751), (24.81204, 121.04969)),
        # ((24.79833, 121.03751), (24.83074, 121.02137)),
        # ((24.78052, 121.00793), (24.79579, 121.02286))
    ]
    
    for sw, ne in ranges:
        lat_range = (min(sw[0], ne[0]), max(sw[0], ne[0]))
        lng_range = (min(sw[1], ne[1]), max(sw[1], ne[1]))
        
        
        grid_search(type='restaurant',
                    lat_range=lat_range, lng_range=lng_range)
    '''
    try:
        start = 87000
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
    
    '''
    auto_download_step2((25.0580211433764, 121.553795038151))
    '''

    '''
    place_info_df = pd.read_csv('data/cids.csv')
    place_info_df['cid'] = place_info_df['cid'].apply(str)
    place_info_list = place_info_df.to_dict('records')

    download_by_place_info_list2(place_info_list)
    '''

    '''
    coordinates = [
        (23.9866451, 121.5909399),
        (23.864951, 121.5177478),
        (23.4637683, 121.3743676),
        (23.0528137, 121.1830295),
        (22.7589683, 121.0935725),
        (22.0075077, 120.7217325),
        (22.2616057, 120.6665648),
        (22.425291, 120.5705847),
        (22.6373232, 120.3168692),
        (22.6160968, 120.3947276),
        (22.7591869, 120.3244133),
        (22.9951395, 120.1979847),
        (23.0289862, 120.2627547),
        (23.1236873, 120.1178188),
        (23.203738, 120.2629049),
        (23.3274147, 120.2605668),
        (23.4938897, 120.4522911),
        (23.8783817, 120.4729763),
        (24.1513546, 120.6570402),
        (24.2703812, 120.6852785),
        (24.576719, 120.8185092)
    ]
    visited_locs = set()
    for co in coordinates:
        visited_locs |= auto_download(
            co, type='restaurant', visited_locs=visited_locs)
    '''
