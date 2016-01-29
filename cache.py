# This file will look up the cached versions of the data in DB and return if available.
# If the data is not available, it will generate it, write to DB and return it to the main process.
import re
from settings import db


def get_main_data(col1, col2):
    cols = '{}_{}'.format(col1, col2)
    if db.cache.find_one({'cached_result': cols}):
        return db.cache.find_one({'cached_result': cols})[cols]
    else:
        return create_main_cache(col1, col2)


def create_main_cache(col1, col2):

    pages1 = db[col1].find()
    context = dict()

    for page1 in pages1:
        page2 = db[col2].find_one({'url': page1['url']})

        if page1 and page2:

            for key in page1:
                if page1.get(key) != page2.get(key):
                    if context.get(key):
                        context[key] += 1
                    else:
                        context[key] = 1

    re_redirects = re.compile(r'^301', re.IGNORECASE)

    context1 = dict()
    context1['col1'] = col1
    context1['errors'] = db[col1].find({'status_code': 404}).count()
    context1['disallowed'] = db[col1].find({'robots_txt': 'Disallowed'}).count()
    context1['noindex'] = db[col1].find({'robots': 'noindex, nofollow'}).count()
    context1['redirects'] = db[col1].find({'redirects': re_redirects}).count()

    context2 = dict()
    context2['col2'] = col2
    context2['errors'] = db[col2].find({'status_code': 404}).count()
    context2['disallowed'] = db[col2].find({'robots_txt': 'Disallowed'}).count()
    context2['noindex'] = db[col2].find({'robots': 'noindex, nofollow'}).count()
    context2['redirects'] = db[col2].find({'redirects': re_redirects}).count()

    cached_result = {'context': context, 'context1': context1, 'context2': context2}

    # write processed result to DB
    cols = '{}_{}'.format(col1, col2)
    db.cache.insert_one({'cached_result': cols, cols: cached_result})

    return cached_result


def check_cache(col1, col2, key):
    cols = '{}_{}'.format(col1, col2)
    if db.cache.find_one({'cached_urls_{}'.format(key): cols}):
        return db.cache.find_one({'cached_urls_{}'.format(key): cols})[cols]
    else:
        return create_urls_cache(col1, col2, key)


def get_urls_data(col1, col2, key=None, urls=None):

    if not urls:
        return check_cache(col1, col2, key)

    # adding URLs filter
    urls_data = check_cache(col1, col2, key)
    pages = urls_data['pages']

    filtered_pages = list()
    if urls == 'bgg':
        bgg_rx = re.compile(r'.+\-bgg\d+')
        for page in pages:
            if re.search(bgg_rx, page['url']):
                filtered_pages.append(page)
    elif urls == 'bgc':
        bgc_rx = re.compile(r'.+\-bgc\d+')
        for page in pages:
            if re.search(bgc_rx, page['url']):
                filtered_pages.append(page)
    elif urls == 'g':
        g_rx = re.compile(r'.+\-g\d.+')
        for page in pages:
            if re.search(g_rx, page['url']):
                filtered_pages.append(page)
    elif urls == 's':
        s_rx = re.compile(r'.+\-s\d+')
        for page in pages:
            if re.search(s_rx, page['url']):
                filtered_pages.append(page)
    elif urls == 'bgr':
        bgr_rx = re.compile(r'.+\-bgr\d+')
        for page in pages:
            if re.search(bgr_rx, page['url']):
                filtered_pages.append(page)
    else:
        filtered_pages = pages

    return {'pages': filtered_pages, 'key': key}


def create_urls_cache(col1, col2, key=None):

    parameters = ['status_code', 'robots_txt', 'redirects', 'b_home_footer', 'description',
                  'b_footer_search_also', 'h2', 'h3', 'title', 'canonical', 'robots', 'b_descr_blocks_item',
                  'p_gsarticle_promo_aside', 'b_left', 'headers', 'b_descr_text', 'keywords', 'error', 'h1',
                  'load_time', 'b_similar', 'size']

    if key in parameters:
        pages = db[col1].find()
        pages_res = list()
        for page1 in pages:
            page2 = db[col2].find_one({'url': page1['url']})
            if page1 and page2:
                if page1.get(key) != page2.get(key):
                    pages_res.append(page1)
        pages = pages_res
    elif key == '404':
        pages = db[col1].find({'status_code': 404})
    elif key == 'rb_txt':
        pages = db[col1].find({'robots_txt': 'Disallowed'})
    elif key == 'rb_meta':
        pages = db[col1].find({'robots': 'noindex, nofollow'})
    elif key == 'redirects':
        pages = db[col1].find({'redirects': re.compile(r'^301', re.IGNORECASE)})
    else:
        pages = db[col1].find()

    pages_result = list()
    pages_result.extend([{'url': x['url'], 'status_code': x['status_code'], '_id': x['_id']} for x in pages])

    cached_result = {'pages': pages_result, 'key': key}

    # write processed result to DB
    cols = '{}_{}'.format(col1, col2)
    db.cache.insert_one({'cached_urls_{}'.format(key): cols, cols: cached_result})

    return cached_result
