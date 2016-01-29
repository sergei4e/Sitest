# This file will look up the cached versions of the data in DB and return if available.
# If the data is not available, it will generate it, write to DB and return it to the main process.
import re
from settings import db


def get_data(col1, col2, key=None, urls=None):

    if not urls and not key:
        return check_cache(col1, col2)

    main_data = check_cache(col1, col2)

    # Page filters
    pages = main_data['pages']
    filtered_pages = pages

    # Keys filter
    if key:
        filtered_pages = list()
        for page in pages:
            if key in page['keys']:
                filtered_pages.append(page)

    # URLs filter
    if urls:
        urls_pages = list()
        if urls == 'bgg':
            bgg_rx = re.compile(r'.+\-bgg\d+')
            for page in filtered_pages:
                if re.search(bgg_rx, page['url']):
                    urls_pages.append(page)
        elif urls == 'bgc':
            bgc_rx = re.compile(r'.+\-bgc\d+')
            for page in filtered_pages:
                if re.search(bgc_rx, page['url']):
                    urls_pages.append(page)
        elif urls == 'g':
            g_rx = re.compile(r'.+\-g\d.+')
            for page in filtered_pages:
                if re.search(g_rx, page['url']):
                    urls_pages.append(page)
        elif urls == 's':
            s_rx = re.compile(r'.+\-s\d+')
            for page in filtered_pages:
                if re.search(s_rx, page['url']):
                    urls_pages.append(page)
        elif urls == 'bgr':
            bgr_rx = re.compile(r'.+\-bgr\d+')
            for page in filtered_pages:
                if re.search(bgr_rx, page['url']):
                    urls_pages.append(page)
        filtered_pages = urls_pages

    return {'context': main_data['context'],
            'context1': main_data['context1'],
            'context2': main_data['context2'],
            'pages': filtered_pages
            }


def check_cache(col1, col2):
    cols = '{}_{}'.format(col1, col2)
    data = db.cache.find_one({'cached_data': cols})
    if data:
        return data[cols]
    else:
        return create_cache(col1, col2)


def create_cache(col1, col2):

    pages = db[col1].find()
    pages_result = list()
    context = dict()
    parameters = ['status_code', 'robots_txt', 'redirects', 'b_home_footer', 'description',
                  'b_footer_search_also', 'h2', 'h3', 'title', 'canonical', 'robots', 'b_descr_blocks_item',
                  'p_gsarticle_promo_aside', 'b_left', 'headers', 'b_descr_text', 'keywords', 'error', 'h1',
                  'load_time', 'b_similar', 'size']

    for page1 in pages:
        page2 = db[col2].find_one({'url': page1['url']})

        # Main data
        if page1 and page2:

            for key in page1:
                if page1.get(key) != page2.get(key):
                    if context.get(key):
                        context[key] += 1
                    else:
                        context[key] = 1

        # URLs data
        keys = list()
        for key in parameters:
            if page1 and page2:
                if page1.get(key) != page2.get(key):
                    keys.append(key)

        if page1['status_code'] == 404:
            keys.append('404')
        elif page1['robots_txt'] == 'Disallowed':
            keys.append('rb_txt')
        elif page1['robots'] == 'noindex, nofollow':
            keys.append('rb_meta')
        elif page1['redirects'] != '301':
            keys.append('redirects')

        pages_result.append({'url': page1['url'], 'status_code': page1['status_code'], '_id': page1['_id'],
                             'keys': keys})

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

    cached_result = {'context': context, 'context1': context1, 'context2': context2, 'pages': pages_result}

    # write processed result to DB
    cols = '{}_{}'.format(col1, col2)
    db.cache.insert_one({'cached_data': cols, cols: cached_result})

    return cached_result
