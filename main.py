# coding: utf-8
from flask import render_template, request, session

import login
from settings import *
from diff import difference

from cache import get_data


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

    if col1 < col2:
        col1, col2 = col2, col1

    main_data = get_data(col1, col2)

    context = main_data['context']
    context1 = main_data['context1']
    context2 = main_data['context2']

    return render_template('index.html', context=context, context1=context1, context2=context2, cols=cols)


@app.route('/urls', methods=['GET', 'POST'])
@login.login_required
def urls():

    col1 = session['col1']
    col2 = session['col2']
    key = request.args.get('f')
    url_type = request.args.get('type')
    session['url_types'] = ['All pages', 'bgg', 'bgc', 'g', 's', 'bgr']

    if not url_type:
        url_type = session['url_type'] = session['url_types'][0]

    urls_data = get_data(col1, col2, key=key, urls=url_type)
    pages = urls_data['pages']

    return render_template('urls.html', pages=pages, url_types=session['url_types'], url_type=url_type, key=key)


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
