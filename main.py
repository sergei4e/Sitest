# coding: utf-8
from flask import render_template, request, session

import login
from settings import *
from diff import difference

from cache import get_data
from db_connect import CollectionItem, Collection


@app.route('/example')
def example():
    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
@login.login_required
def index():

    session['cols'] = [x.date for x in db.query(Collection).all()]
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

    main_data = get_data(col1, col2)
    keys = main_data.keys()

    return render_template('index.html', data=main_data, keys=keys)


@app.route('/urls', methods=['GET', 'POST'])
@login.login_required
def urls():

    col1 = session['col1']
    col2 = session['col2']
    key = request.args.get('f')
    url_type = request.args.get('type')

    # session['url_types'][0] value must always be the default one, meaning no filters enabled
    session['url_types'] = ['All pages', 'bgg', 'bgc', 'g', 's', 'bgr']

    if not url_type:
        url_type = session['url_type'] = session['url_types'][0]

    urls_data = get_data(col1, col2, key=key, urls=url_type)
    pages = urls_data.pages

    return render_template('urls.html', pages=pages, url_types=session['url_types'], url_type=url_type, key=key)


@app.route('/urls/<ID>')
@login.login_required
def one_url(ID):

    col1 = session['col1']
    col2 = session['col2']

    page1 = db.query(CollectionItem).filter(CollectionItem.id == ID, Collection.date == col1).one()
    page2 = db.query(CollectionItem).filter(CollectionItem.url == page1.url, Collection.date == col2).one()

    for key in page1.__dict__:
        if key == '_sa_instance_state':
            continue

        if isinstance(page1.key, unicode):
            diff = difference(getattr(page1, key), getattr(page2, key))
            setattr(page1, key, diff[0])
            setattr(page2, key, diff[1])

    return render_template('url.html', page1=page1, page2=page2, col1=col1, col2=col2)


if __name__ == "__main__":
    app.run()
