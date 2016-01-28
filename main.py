# coding: utf-8
import re

from flask import render_template, request, session

import login
from settings import *
from diff import difference


@app.route('/example')
def example():
    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
@login.login_required
def index():

    session['cols'] = [x for x in db.collection_names(include_system_collections=False) if x.startswith('20')]
    session['cols'].sort()
    session['cols'].reverse()
    cols = session['cols']

    if not session.get('col1'):
        col1 = session['col1'] = session['cols'][0]
        col2 = session['col2'] = session['cols'][1]
    else:
        col1 = session['col1']
        col2 = session['col2']

    if request.method == 'POST':
        col1 = session['col1'] = request.form.get('col1')
        col2 = session['col2'] = request.form.get('col2')

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

    regx = re.compile(r'^301', re.IGNORECASE)

    context1 = dict()
    context1['col1'] = col1
    context1['errors'] = db[col1].find({'status_code': 404}).count()
    context1['disalloved'] = db[col1].find({'robots_txt': 'Disallowed'}).count()
    context1['noindex'] = db[col1].find({'robots': 'noindex, nofollow'}).count()
    context1['redirects'] = db[col1].find({'redirects': regx}).count()

    context2 = dict()
    context2['col2'] = col2
    context2['errors'] = db[col2].find({'status_code': 404}).count()
    context2['disalloved'] = db[col2].find({'robots_txt': 'Disallowed'}).count()
    context2['noindex'] = db[col2].find({'robots': 'noindex, nofollow'}).count()
    context2['redirects'] = db[col2].find({'redirects': regx}).count()

    return render_template('index.html', context=context, context1=context1, context2=context2, cols=cols)


@app.route('/urls', methods=['GET', 'POST'])
@login.login_required
def urls():
    
    key = ''
    col1 = session['col1']
    col2 = session['col2']
    pages = db[col1].find()

    parameters = ['status_code', 'robots_txt', 'redirects', 'b_home_footer', 'description',
                  'b_footer_search_also', 'h2', 'h3', 'title', 'canonical', 'robots', 'b_descr_blocks_item',
                  'p_gsarticle_promo_aside', 'b_left', 'headers', 'b_descr_text', 'keywords', 'error', 'h1',
                  'load_time', 'b_similar', 'size']

    if request.args.get('f') in parameters:
        pages = list()
        key = request.args.get('f')
        pages1 = db[col1].find()
        for page1 in pages1:
            page2 = db[col2].find_one({'url': page1['url']})
            if page1 and page2:
                if page1.get(key) != page2.get(key):
                    pages.append(page1)
    elif request.args.get('f') == '404':
        pages = db[col1].find({'status_code': 404})
    elif request.args.get('f') == 'rb_txt':
        pages = db[col1].find({'robots_txt': 'Disallowed'})
    elif request.args.get('f') == 'rb_meta':
        pages = db[col1].find({'robots': 'noindex, nofollow'})
    elif request.args.get('f') == 'redirects':
        pages = db[col1].find({'redirects': re.compile(r'^301', re.IGNORECASE)})

    return render_template('urls.html', pages=pages, key=key)


@app.route('/urls/<ID>')
@login.login_required
def one_url(ID):

    col1 = session['col1']
    col2 = session['col2']

    page1 = db[col1].find_one({'_id': ObjectId(ID)})
    page2 = db[col2].find_one({'url': page1['url']})

    # '''
    for key in page1:
        if type(page1[key]) is list or type(page2[key]) is list:
            page1[key], page2[key] = u' '.join(page1[key]), u' '.join(page2[key])

        if type(page1[key]) is dict or type(page2[key]) is dict:
            page1[key], page2[key] = unicode(page1[key]), unicode(page2[key])

        if type(page1[key]) is unicode:
            page1[key], page2[key] = difference(page1[key], page2[key])  # '''

    return render_template('url.html', page1=page1, page2=page2, col1=col1, col2=col2)


if __name__ == "__main__":
    app.run()
