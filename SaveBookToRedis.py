#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = 'redis发布者'
__author__ = 'Mad Dragon'
__mtime__ = '2019/1/12'
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
import time

import moment
import redis

from public.ConfigParser import ConfigParser
from public.DataToo import DataToo
from public.MySqlToo import MySqlToo
from public.RedisToo import RedisToo
from public.TimeToo import TimeToo
from public.Logger import Logger


class SaveBookToRedis():
    def __init__(self, environmentalType, maxBookNex):
        self.b_title = 'SaveBookToRedis'
        self.b_bookPageSize = 10
        self.b_bookIdSize = 5
        self.b_bookTXTGroupSize = 100
        self.b_second = 1
        self.b_environmentalType = int(environmentalType)
        self.b_maxBookNex = int(maxBookNex)

        self.b_catalogList = []
        self.b_bookTXTData = []
        self.errorUrl = []
        self.request404 = []
        self.countNum = 0

        self.con = ConfigParser()
        self.logName = self.intLogName()
        self.rds = RedisToo()
        self.mySql = MySqlToo(logName=self.logName)
        self.dataToo = DataToo(logName=self.logName, second=self.b_second)
        self.logger = Logger(logname=self.logName, loglevel=1, logger=self.b_title).getlog()
        self.timeToo = TimeToo()
        self.b_mysqlStr = self.initMysqlStr()

    def initMysqlStr(self):
        if self.b_environmentalType == 2:
            environmental = 'online'
            getBookIdsSql = "SELECT book_Id FROM books WHERE nex > %s" % self.b_maxBookNex
        elif self.b_environmentalType == 1:
            environmental = 'test'
            testBookId = '10000,20000'
            getBookIdsSql = "SELECT book_Id FROM books WHERE nex > %s limit %s" % (self.b_maxBookNex, testBookId)
        else:
            environmental = 'dev'
            testBookId = "'10000611804961003','10000828104982003'"
            getBookIdsSql = "SELECT book_Id FROM books WHERE book_Id in (%s)" % testBookId
            self.b_bookPageSize = 2
            self.b_bookIdSize = 2
            self.b_bookTXTGroupSize = 1

        return {
            'saveText': "INSERT INTO `links` (`url`,article) VALUES (%s, %s) ON DUPLICATE KEY UPDATE article = VALUES (article), nex = nex+1",
            'getBookIdsSql': getBookIdsSql,
            'getCatalogData': "SELECT url FROM links WHERE fs = 0 AND book_Id in "
        }

    def intLogName(self):
        timeStr = moment.now().format('YYYY-MM-DD-HH-mm-ss')
        return '%s_%s.log' % (self.b_title, timeStr)

    def second(self):
        time.sleep(self.b_second)

    def getBookData(self):
        bookList = []
        bookData = self.mySql.getListData(sql=self.b_mysqlStr['getBookIdsSql'])
        for item in bookData:
            bookList.append(item[0])
        return bookList

    def setCatalogList(self, bookGroupingData):
        bookData = bookGroupingData['listTaskList']
        if len(bookData) <= 0:
            self.logger.debug('setCatalogList 没有数据\n')
            return
        bookIdGroupingData = self.dataToo.groupingData(list=bookData, pageSize=self.b_bookIdSize)
        listTaskList = bookIdGroupingData['listTaskList']
        for i in range(bookIdGroupingData['listGroupSize']):
            if len(listTaskList[i]) <= 0: continue
            data = []
            for item in listTaskList[i]:
                data.append(','.join(item))
            self.rds.setListData('bookIdsList', data)

    def bookTxtLoad(self):
        start = time.time()
        bookData = self.getBookData()
        if len(bookData) <= 0:
            self.logger.debug('bookTxtLoad 没有数据\n')
            return
        bookGroupingData = self.dataToo.groupingData(list=bookData, pageSize=self.b_bookPageSize)
        self.setCatalogList(bookGroupingData)

        end = time.time()
        self.logger.info('========' * 15)
        self.logger.info("startTime: %s" % (moment.now().format('YYYY-MM-DD HH:mm:ss')))
        self.logger.info("webHost：%s" % (self.con.getConfig('webConfig', 'host')))
        self.logger.info("author：%s" % (self.con.getConfig('webConfig', 'author')))
        self.logger.info("email：%s" % (self.con.getConfig('webConfig', 'email')))
        self.logger.info('本次将采集 [ %s ] 本小说，共分为 %s 个组,每组 %s 本小说。' % (
            bookGroupingData['listSize'], bookGroupingData['listGroupSize'], bookGroupingData['listTaskSize']))
        self.logger.info('saveBooksToRedis [ %s ] 组 小说，消耗时间：%s 秒 [ %s ]' % (
            bookGroupingData['listGroupSize'],
            float(end) - float(start),
            self.timeToo.changeTime(float(end) - float(start))))
        self.logger.info('========' * 15)


if __name__ == '__main__':

    environmentalType = input("请输入0、1、2（0：dev,1:test,2:online）: >>")
    maxBookNex = 0
    print(
        '\n\n参数确认： 环境 : %s | 最大抓取数 : %s \n\n' % (environmentalType, maxBookNex))
    time.sleep(1)
    isStart = input("是否开始？(y/n): >>")
    if (isStart == 'y'):
        book = SaveBookToRedis(environmentalType=environmentalType, maxBookNex=maxBookNex)
        book.bookTxtLoad()
    else:
        print('取消抓取')
