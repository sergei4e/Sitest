# coding: utf-8

from lxml import html
from . import logger


def check_meta_robots(page):
        tree = html.fromstring(page)
        robots = tree.xpath(u'//meta[@name="robots"]/@content')
        if not robots:
            return True, True
        robots = robots[0].split(u',')  # list --> srt --> list
        if len(robots) == 2:
            index = robots[0].strip()
            follow = robots[1].strip()
        elif len(robots) == 1:
            index = robots[0].strip()
            follow = True
        else:
            return True, True
        logger.debug(u'Meta robots: {}, {}'.format(index, follow))
        if index == u'none':
            index, follow = False, False
        if index == u'all':
            index, follow = True, True
        if index == u'noindex':
            index = False
        if index == u'index':
            index = True
        if follow == u'nofollow':
            follow = False
        if follow == u'follow':
            follow = True
        if type(index) != bool:
            index = True
        if type(follow) != bool:
            follow = True
        logger.debug(u'Meta robots: {}, {}'.format(index, follow))
        return index, follow
