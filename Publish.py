#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
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

from public.DataToo import DataToo
from public.Logger import Logger
from public.RedisToo import RedisToo


class Publish():
    def __init__(self):
        self.b_title = 'Publish'
        self.b_second = 1
        self.b_timeStr = moment.now().format('YYYY-MM-DD-HH-mm-ss')

        self.rds = RedisToo()
        self.dataToo = DataToo(logName=self.b_title, second=self.b_second, timeStr=self.b_timeStr)
        self.logger = Logger(logname=self.dataToo.initLogName(), loglevel=1, logger=self.b_title).getlog()

    def saveBookToRedisAction(self):
        environmentalType = input("请输入0、1、2（0：dev,1:test,2:online）: >>")
        maxBookNex = 0
        self.logger.debug(
            '\n\n参数确认: 环境 : %s | 最大抓取数 : %s \n\n' % (environmentalType, maxBookNex))
        time.sleep(1)
        isStart = input("是否开始？(y/n): >>")
        if (isStart == 'y'):
            self.rds.p.publish('bookChannel', str(
                json.dumps({'type': 'SaveBookToRedis', 'environmentalType': environmentalType, 'maxBookNex': maxBookNex
                            })))
        else:
            print('取消抓取')

    def getBookTXTAction(self):
        getBookIdsListSize = input("获取多少组数据（最大10）: >>")
        maxCatalogNex = 1
        print(
            '\n\n参数确认： maxCatalogNex : %s | getBookIdsListSize : %s \n\n' % (maxCatalogNex, getBookIdsListSize))
        time.sleep(1)
        isStart = input("是否开始？(y/n): >>")
        if (isStart == 'y'):
            self.rds.p.publish('bookChannel', str(json.dumps(
                {'type': 'GetBookTXT', 'maxCatalogNex': maxCatalogNex, 'getBookIdsListSize': getBookIdsListSize})))
        else:
            print('取消抓取')


if __name__ == '__main__':
    publish = Publish()
    while True:
        publish.logger.debug('0:初始化数据')
        publish.logger.debug('1:发布抓取文章通知')
        publish.logger.debug('stop:停止所有订阅者运行')
        publish.logger.debug('0:初始化数据')
        time.sleep(1)
        directive = input("publish: >>")

        if directive == "0":
            publish.logger.debug("初始化数据")
            time.sleep(1)
            publish.saveBookToRedisAction()
        if directive == "1":
            publish.logger.debug("发布抓取文章通知")
            time.sleep(1)
            publish.getBookTXTAction()
        if directive == "stop":
            publish.logger.debug("停止所有订阅者运行")
            publish.rds.p.publish('bookChannel', str(json.dumps({'type': 'stop'})))
            break
