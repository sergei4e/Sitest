# This file will look up the cached versions of the data in DB and return if available.
# If the data is not available, it will generate it, write to DB and return it to the main process.
import re
from settings import db
from flask import session
from db_connect import Collection, CollectionItem, Cache, CachePage


def get_data(col1, col2, key=None, urls=None):

    if urls == session['url_types'][0]:
        urls = None
    if not urls and not key:
        return check_cache(col1, col2)
    else:
        return filter_pages(col1, col2, key, urls)


def filter_pages(col1, col2, key, urls):

    main_data = check_cache(col1, col2)

    # Page filters

    filtered_pages = main_data.pages

    # Keys filter
    if key:
        urls_pages = []
        for page in main_data.pages:
            if key in page.__dict__:
                urls_pages.append(page)
        filtered_pages = urls_pages

    # URLs filter
    if urls:
        urls_pages = []
        if urls == 'bgg':
            bgg_rx = re.compile(r'.+\-bgg\d+')
            for page in filtered_pages:
                if re.search(bgg_rx, page.url):
                    urls_pages.append(page)
        elif urls == 'bgc':
            bgc_rx = re.compile(r'.+\-bgc\d+')
            for page in filtered_pages:
                if re.search(bgc_rx, page.url):
                    urls_pages.append(page)
        elif urls == 'g':
            g_rx = re.compile(r'.+\-g\d.+')
            for page in filtered_pages:
                if re.search(g_rx, page.url):
                    urls_pages.append(page)
        elif urls == 's':
            s_rx = re.compile(r'.+\-s\d+')
            for page in filtered_pages:
                if re.search(s_rx, page.url):
                    urls_pages.append(page)
        elif urls == 'bgr':
            bgr_rx = re.compile(r'.+\-bgr\d+')
            for page in filtered_pages:
                if re.search(bgr_rx, page.url):
                    urls_pages.append(page)
        filtered_pages = urls_pages

    main_data.pages = filtered_pages

    return main_data


def check_cache(start_date, end_date):
    if start_date < end_date:
        start_date, end_date = end_date, start_date

    cache = db.query(Cache).filter(Cache.start_date == start_date,
                                   Cache.end_date == end_date).one_or_none()

    if cache:
        return cache
    else:
        return create_cache(start_date, end_date)


def create_cache(col1, col2):

    cache = Cache(start_date=col1, end_date=col2)
    cache.pages = []

    pages = db.query(Collection).filter(Collection.date == col1).all()

    parameters = ['status_code', 'robots_txt', 'redirects', 'b_home_footer', 'description',
                  'b_footer_search_also', 'h2', 'h3', 'title', 'canonical', 'robots', 'b_descr_blocks_item',
                  'p_gsarticle_promo_aside', 'b_left', 'headers', 'b_descr_text', 'keywords', 'error', 'h1',
                  'load_time', 'b_similar', 'size']

    for page1 in pages:
        page2 = db.query(Collection).filter(Collection.date == col2, CollectionItem.url == page1.url).one_or_none()

        # Main data
        if page1 and page2:

            for key in page1.__dict__:
                if key.startswith('_'):
                    continue
                if getattr(page1, key, None) != getattr(page2, key, None):
                    if getattr(cache, key, None):
                        cache.__dict__[key] += 1
                    else:
                        setattr(cache, key, 1)

        # URLs data
        keys = []
        for key in parameters:
            if page1 and page2:
                if getattr(page1, key, None) != getattr(page2, key, None):
                    keys.append(key)

        if page1.status_code == 404:
            keys.append('404')
        elif page1.robots_txt == 'Disallowed':
            keys.append('rb_txt')
        elif page1.robots == 'noindex, nofollow':
            keys.append('rb_meta')
        elif page1.redirects != '301':
            keys.append('redirects')

        cache_page = CachePage(url=page1.url, status_code=page1.status_code)
        for k in keys:
            setattr(cache_page, k, True)

        cache.pages.append(cache_page)

    re_redirects = re.compile(r'^301', re.IGNORECASE)

    cache.errors_1 = \
        db.query(Collection).filter(Collection.items == col1, CollectionItem.status_code == 404).count()
    cache.disallowed_1 = \
        db.query(Collection).filter(Collection.items == col1, CollectionItem.robots_txt == 'Disallowed').count()
    cache.noindex_1 = \
        db.query(Collection).filter(Collection.items == col1, CollectionItem.robots == 'noindex, nofollow').count()
    cache.redirects_1 = \
        db.query(Collection).filter(Collection.items == col1, CollectionItem.redirects == re_redirects).count()

    cache.errors_2 = \
        db.query(Collection).filter(Collection.items == col2, CollectionItem.status_code == 404).count()
    cache.disallowed_2 = \
        db.query(Collection).filter(Collection.items == col2, CollectionItem.robots_txt == 'Disallowed').count()
    cache.noindex_2 = \
        db.query(Collection).filter(Collection.items == col2, CollectionItem.robots == 'noindex, nofollow').count()
    cache.redirects_2 = \
        db.query(Collection).filter(Collection.items == col2, CollectionItem.redirects == re_redirects).count()

    db.add(cache)
    db.commit()

    return cache
