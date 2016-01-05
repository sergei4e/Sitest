# coding: utf-8
import threading
import logging
logger = logging.getLogger()

from pars.crawler import Parser
from pars.settings import Settings

Settings.START_LINK = 'http://kharkov.all.biz/'
Settings.DB_NAME = 'allbiztest'
se = Settings()
se.THREADS = 10
se.TIMEOUT = 40
Parser.settings = se

with open('urls.txt', 'r') as f:
    Parser.urls_new = f.read().split('\r\n')


def worker():
    th = list()
    for _ in range(Parser.settings.THREADS):
        p = Parser()
        t = threading.Thread(target=p.parser)
        t.start()
        th.append(t)  # '''

    '''
    while True:
        print u"Чтобы остановить парсинг введите - S (Stop)\n"
        ex = raw_input()
        if ex.lower() == 's':
            Parser.stop_flag = True
            break  # '''

    for t in th:
        t.join()

    Parser().scan_errors()

    print u'*******Сканирование прекращено*******'
    print u'Успел отсканировать: {}'.format(len(Parser.urls_old))
    print u'Осталось в очереди на сканирование: {}'.format(len(Parser.urls_new))
    print u'*******Ошибок всего: {}*******'.format(len(Parser.errors))

if __name__ == '__main__':
    worker()
