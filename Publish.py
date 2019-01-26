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

from public.DataTool import DataTool
from public.Logger import Logger
from public.RedisTool import RedisTool


class Publish():
    def __init__(self):
        self.b_title = 'Publish'
        self.b_second = 1
        self.b_timeStr = moment.now().format('YYYY-MM-DD-HH-mm-ss')
        self.b_rdsKeyName = 'bookIdsList'
        self.rds = RedisTool()
        self.dataTool = DataTool(logName=self.b_title, second=self.b_second, timeStr=self.b_timeStr)
        self.logger = Logger(logname=self.dataTool.initLogName(), loglevel=1, logger=self.b_title).getlog()

    def saveBookToRedisAction(self):

        environmental = ['dev', 'test', 'online']
        print('可选环境：')
        for i in range(len(environmental)):
            print('\t\t%s : %s' % (i, environmental[i]))

        environmentalType = int(input("请输入0、1、2: >>"))
        print(
            '参数确认： 环境 : %s \n' % (environmental[environmentalType]))
        time.sleep(1)
        isStart = input("是否开始？(y/n): >>")
        if (isStart == 'y'):
            self.rds.p.publish('bookChannel', str(
                json.dumps(
                    {'type': 'SaveBookToRedis', 'environmentalType': environmentalType, 'rdsKeyName': self.b_rdsKeyName
                     })))
        else:
            print('取消抓取')

    def getBookTXTAction(self):
        getBookIdsListSize = input("每次获取多少条链接（最大1000）: >>")
        print(
            '\n\n参数确认： rdsKeyName : %s | getBookIdsListSize : %s \n\n' % (self.b_rdsKeyName, getBookIdsListSize))
        time.sleep(1)
        isStart = input("是否开始？(y/n): >>")
        if (isStart == 'y'):
            self.rds.p.publish('bookChannel', str(json.dumps(
                {'type': 'GetBookTXT', 'getBookIdsListSize': getBookIdsListSize, 'rdsKeyName': self.b_rdsKeyName})))
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
