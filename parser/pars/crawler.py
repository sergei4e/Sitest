# coding: utf-8
import time
import requests
from selenium import webdriver
from lxml import html
from datetime import date, datetime

from settings import Settings

import logging
FORMAT = '%(levelname)s : %(asctime)s : %(funcName)s : %(lineno)d : %(message)s'
logging.basicConfig(format=FORMAT, filename='pars.log')
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

from __init__ import html_chenger
from threading import Lock
l = Lock()


class Parser(object):
    settings = Settings()
    urls_new = list()
    urls_old = list()
    errors = list()
    count = 0
    stop_flag = False

    logger.debug(u'Вызван класс Parser, закеширован robots и инициализировано соединение с базой')

    def __init__(self):
        if Parser.count == 0:
            self.url = Parser.settings.START_LINK
        self.robots, self.redirects, self.page, self.error = [], [], '', ''
        self.result, self.page_load_time, self.status_code, self.headers = {}, 0, 0, {}
        self.domain = Parser.settings.DOMAIN
        self.regulars = Parser.settings.REGULARS
        logger.debug(u'Создан инстанс класса Parser')

    def set_elements(self):
        self.result[u'url'] = self.url
        self.result[u'load_time'] = self.page_load_time
        self.result[u'size'] = len(self.page)
        self.result[u'redirects'] = '\n'.join(self.redirects)
        self.result[u'headers'] = self.headers
        if Parser.settings.rules.allowed(self.url, Parser.settings.AGENT):
            self.result[u'robots_txt'] = u'Allowed'
        else:
            self.result[u'robots_txt'] = u'Disallowed'
        self.result[u'status_code'] = self.status_code
        self.result[u'error'] = self.error
        logger.debug(u'Установил url, load_time, size, links, in_links, out_links для {}'.format(self.url))

    def get_elements(self):
        # Parse html page by XPath
        tree = html.fromstring(self.page)
        for page_element in self.regulars:
            content = tree.xpath(self.regulars[page_element])
            self.result[page_element] = html_chenger(content)
        logger.debug(u'Спарсил элементы и записал в словарь result')

    def save(self):
        # Save result in Mongodb
        with l:
            Parser.settings.db[Parser.settings.col_name].insert_one(self.result)
        logger.debug(u'Сохраняю результат в базу данных')

    def clean(self):
        self.page, self.url, self.page_load_time, self.robots, self.error, = '', '', 0, [], ''
        self.status_code, self.headers, self.redirects = 0, {}, []
        self.result = dict()
        logger.debug(u'Сбрасываем параметры result, page, page_load_time, links, robots, errors')

    def get_request(self):
        try:
            response = requests.get(self.url)
            self.status_code = response.status_code
            self.headers = response.headers
            if response.history:
                for resp in response.history:
                    self.redirects.append(unicode(resp.status_code) + u' : ' + unicode(resp.headers['Location']))
        except Exception:
            self.error = 'Error in request'
            logger.debug(u'При открытии url: {} в request произошла ошибка'.format(self.url))

    def open_url(self):
        try:
            browser = webdriver.PhantomJS()
            browser.set_page_load_timeout(Parser.settings.TIMEOUT)
            time1 = time.time()
            browser.get(self.url)
            time2 = time.time()
            self.page = browser.page_source.encode('utf-8')
            browser.quit()
            self.page_load_time = time2 - time1
            logger.debug(u'Url открыт успешно')
        except Exception, e:
            self.error = 'Error in webdriver get'
            with l:
                Parser.errors.append(self.url)
            print u'[Error] Страница {} не загрузилась'.format(self.url)
            logger.error(u'Страница {} не загрузилась браузером'.format(self.url))
            logger.error(e, exc_info=True)

    def parser(self):
        while Parser.urls_new:
            with l:
                self.url = Parser.urls_new.pop()
            if self.url not in Parser.urls_old:
                with l:
                    Parser.urls_old.append(self.url)
                self.get_request()
                self.open_url()
                if self.page:
                    self.get_elements()
                    self.set_elements()
                    self.save()
                    with l:
                        Parser.count += 1
                    print u'[{}] Отсканировал и сохранил url {}'.format(Parser.count, self.url)
                    logger.debug(u'[{}] Отсканировал и сохранил url {}'.format(Parser.count, self.url))
                else:
                    with l:
                        Parser.errors.append(self.url)
                    logger.debug(u'При открытии url: {} произошла ошибка'.format(self.url))
                self.clean()
            else:
                logger.debug(u'url: {} уже был отсканирован ранее'.format(self.url))
            if Parser.stop_flag:
                logger.debug(u'Работа парсера завершена url: {}'.format(self.url))
                break
        print u'Поток отсканировал {}'.format(len(Parser.urls_old))

    def scan_errors(self, num=5):
        for _ in range(num):
            if Parser.errors:
                logger.debug(u'Запушена обработка ошибок')
                with l:
                    Parser.urls_new = Parser.errors
                    for url in Parser.errors:
                        if url in Parser.urls_old:
                            Parser.urls_old.remove(url)
                            logger.debug(u'Будет отсканирован снова: {}'.format(url))
                    Parser.errors = []
                    Parser.stop_flag = False
                self.parser()
                with l:
                    Parser.stop_flag = True
        logger.debug(u'Обработка ошибок завершена')


if __name__ == '__main__':
    par = Parser()
    Parser.urls_new.append('http://kiev.all.biz/avtokreslo-brit-evolva-123-plus-g2791625')
    par.parser()
    print par.result
    print "All Done"
