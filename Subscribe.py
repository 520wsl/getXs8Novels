#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = '接受者'
__author__ = 'Mad Dragon'
__mtime__ = '2019/1/20'
# 我不懂什么叫年少轻狂，只知道胜者为王
              ┏┓      ┏┓
            ┏┛┻━━━┛┻┓
            ┃      ☃      ┃
            ┃  ┳┛  ┗┳  ┃
            ┃      ┻      ┃
            ┗━┓      ┏━┛
                ┃      ┗━━━┓
                ┃  神兽保佑    ┣┓
                ┃　永无BUG！   ┏┛
                ┗┓┓┏━┳┓┏┛
                  ┃┫┫  ┃┫┫
                  ┗┻┛  ┗┻┛
"""
import json
import time

import moment
import redis

from SaveBookToRedis import SaveBookToRedis
from getBookTXT import GetBookTXT
from public.DataToo import DataToo
from public.Logger import Logger
from public.RedisToo import RedisToo


class Subscribe():
    def __init__(self):
        self.b_title = 'Subscribe'
        self.b_second = 1
        self.b_timeStr = moment.now().format('YYYY-MM-DD-HH-mm-ss')

        self.rds = RedisToo()
        self.dataToo = DataToo(logName=self.b_title, second=self.b_second, timeStr=self.b_timeStr)
        self.logger = Logger(logname=self.dataToo.initLogName(), loglevel=1, logger=self.b_title).getlog()

    def saveBookToRedisAction(self, params):
        self.logger.debug(params)
        book = SaveBookToRedis(environmentalType=params['environmentalType'], maxBookNex=params['maxBookNex'])
        book.bookTxtLoad()
        self.logger.debug('saveBookToRedisAction处理结束')

    def getBookTXTAction(self, params):
        self.logger.debug(params)
        book = GetBookTXT(maxCatalogNex=params['maxCatalogNex'], getBookIdsListSize=params['getBookIdsListSize'])
        book.contentsLoad()
        self.logger.debug('getBookTXT处理结束')


if __name__ == '__main__':
    s = Subscribe()
    p = s.rds.p.pubsub()
    p.subscribe("bookChannel")
    for item in p.listen():
        s.logger.debug("Listen on channel : %s " % item['channel'].decode())
        if item['channel'].decode() == "bookChannel":
            if item['type'] == 'message':
                data = item['data'].decode()
                s.logger.debug(data)
                params = json.loads(data)
                s.logger.debug(
                    "getBookTXT: From %s get message : %s" % (item['channel'].decode(), item['data'].decode()))
                if params['type'] == 'SaveBookToRedis':
                    s.saveBookToRedisAction(params)
                if params['type'] == 'GetBookTXT':
                    s.getBookTXTAction(params)
                if params['type'] == 'stop':
                    s.logger.debug(' %s %s' % (item['channel'].decode(), '发布停止运行命令'))
                    break
        if item['channel'] == "order":
            print("order: From %s get message : %s" % (item['channel'].decode(), item['data'].decode()))

    p.unsubscribe('spub')
