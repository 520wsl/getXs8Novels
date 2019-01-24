#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = '文章抓取'
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
import math
import random
import threading
import moment
import time

import redis
from lxml import etree

from GetBookInfoToo import GetBookInfoToo
from public.MySqlToo import MySqlToo
from public.Logger import Logger
from public.DataToo import DataToo
from public.ConfigParser import ConfigParser
from public.RedisToo import RedisToo
from public.TimeToo import TimeToo


class GetBookTXT(object):
    def __init__(self, maxCatalogNex, getBookIdsListSize):
        self.b_getBookIdsListSize = int(getBookIdsListSize)
        self.b_bookPageSize = 10
        self.b_bookIdSize = 5
        self.b_bookTXTGroupSize = 10
        self.b_fs = 0
        self.b_maxCatalogNex = int(maxCatalogNex)
        self.b_title = 'getBookTXT'
        self.b_second = 1
        self.b_timeStr = moment.now().format('YYYY-MM-DD-HH-mm-ss')

        self.b_catalogList = []
        self.b_bookTXTData = []
        self.errorUrl = []
        self.request404 = []
        self.countNum = 0

        self.con = ConfigParser()
        self.dataToo = DataToo(logName=self.b_title, second=self.b_second, timeStr=self.b_timeStr)
        self.mySql = MySqlToo(logName=self.dataToo.initLogName())
        self.logger = Logger(logname=self.dataToo.initLogName(), loglevel=1, logger=self.b_title).getlog()
        self.rds = RedisToo()
        self.timeToo = TimeToo()
        self.getBookInfoToo = GetBookInfoToo()
        self.b_mysqlStr = self.initMysqlStr()

    def initMysqlStr(self):
        return {
            'saveText': "INSERT INTO `links` (`url`,article) VALUES (%s, %s) ON DUPLICATE KEY UPDATE article = VALUES (article), nex = nex+1",
            'getCatalogData': "SELECT url FROM links WHERE fs = %s  AND nex < %s AND book_Id in " % (
                self.b_fs, self.b_maxCatalogNex)
        }

    def target(self):
        bookList = []
        for i in range(self.b_getBookIdsListSize):
            link = self.rds.r.lpop("bookIdsList")
            if link != None:
                link = link.decode(encoding='utf-8')
                bookList.append(link)
        return bookList

    # 2、调用mySQL类 mysqlUtils.getListData 获取数据列表
    def getBookData(self):
        bookLists = self.target()
        bookList = []
        for item in bookLists:
            for item2 in item.split(","):
                bookList.append(item2)
        return bookList

    def getCatalogData(self, bookId, index):
        catalogList = []
        sql = '%s %s' % (self.b_mysqlStr['getCatalogData'], self.dataToo.listToStr(bookId))
        self.logger.info('查询小说章节 [ %s ]...\n' % (sql))
        catalogData = self.mySql.getListData(sql=sql)
        for item in catalogData:
            catalogList.append(item[0])
        self.b_catalogList.append(catalogList)

    #     4、 章节目录 catalog 数据整理 数组
    def setCatalogList(self, bookGroupingData):
        bookData = bookGroupingData['listTaskList']
        if len(bookData) <= 0:
            self.logger.debug('setCatalogList 没有数据\n')
            return
        bookIdGroupingData = self.dataToo.groupingData(list=bookData, pageSize=self.b_bookIdSize)
        listTaskList = bookIdGroupingData['listTaskList']
        for i in range(bookIdGroupingData['listGroupSize']):
            if len(listTaskList[i]) <= 0: continue
            self.dataToo.threads(listTaskList[i], self.getCatalogData)

    def getArticle(self, link):
        content = self.getBookInfoToo.getBookTxtInfo(link)
        if len(content) <= 0:
            self.countNum += 1
            return
        res = self.mySql.batchAdd(sql=self.b_mysqlStr['saveText'], data_info=[(link, content)])
        if res:
            self.errorUrl.append(link)
        self.countNum += 1
        self.logger.debug('第 %s 条链接： %s\n' % (self.countNum, res))
        self.b_bookTXTData.append((link, content))

    #     6、循环调用 getBookTxt()

    # 根据章节 catalogId、url 抓取页面数据
    def getBookTXT(self, catalogList, index):
        if len(catalogList) <= 0:
            self.logger.debug('书籍组 [ %s / %s ] ：getBookTXT 没有数据\n' % (index + 1, len(self.b_catalogList)))
            return
        bookCatalogUrlGroupingData = self.dataToo.groupingData(list=catalogList, pageSize=self.b_bookTXTGroupSize,
                                                               fixed=True)
        listTaskList = bookCatalogUrlGroupingData['listTaskList']
        for i in range(bookCatalogUrlGroupingData['listGroupSize']):
            if len(listTaskList[i]) <= 0:
                self.logger.debug('书籍组 [ %s / %s ] 目录组 [ %s / %s ] ：bookCatalogUrlGroupingData 没有数据\n' % (
                    index + 1, len(self.b_catalogList), i + 1, bookCatalogUrlGroupingData['listGroupSize']))
                continue
            start = time.time()
            for j in range(len(listTaskList[i])):
                time.sleep(self.b_second)
                self.getArticle(listTaskList[i][j])
            end = time.time()
            self.logger.debug('书籍组 [ %s / %s ] 目录组 [ %s / %s ] : 开始时间：%s ： 结束时间：%s ==> 共消耗时间 ：%s 秒 [ %s ]\n' % (
                index + 1, len(self.b_catalogList), i + 1, bookCatalogUrlGroupingData['listGroupSize'],
                float(start), float(end), int(float(end) - float(start)),
                self.timeToo.changeTime(int(float(end) - float(start)))))

    def saveText(self):
        for i in range(len(self.b_catalogList)):
            if len(self.b_catalogList[i]) <= 0:
                self.logger.debug('书籍组 [ %s / %s ] saveText 没有数据\n' % (i + 1, len(self.b_catalogList)))
                continue
            start = time.time()
            self.getBookTXT(self.b_catalogList[i], i)
            end = time.time()
            self.logger.debug('书籍组 [ %s / %s ] : 开始时间：%s ： 结束时间：%s ==> 共消耗时间 ：%s 秒 [ %s ]\n' % (
                i + 1, len(self.b_catalogList), float(start), float(end), int(float(end) - float(start)),
                self.timeToo.changeTime(int(float(end) - float(start)))))
            self.logger.info('*-*-*-*-*-*-' * 15)
            # res = mySql.batchAdd(sql=self.b_mysqlStr['saveText'], data_info=self.b_bookTXTData)
            # if res: self.b_bookTXTData = []

    # 文章内容存储
    def bookTxtLoad(self, bookData):
        start = time.time()
        bookGroupingData = self.dataToo.groupingData(list=bookData, pageSize=self.b_bookPageSize)

        self.logger.info('========' * 15)
        self.logger.info("\t时间: %s" % (moment.now().format('YYYY-MM-DD HH:mm:ss')))
        self.logger.info("\t网站：%s" % (self.con.getConfig('webConfig', 'host')))
        self.logger.info("\t\t\t本次将采集 %s 本小说。\n" % (bookGroupingData['listSize']))
        self.logger.info('\t\t\t%s 本小说，共分为 %s 个组,每组 %s 本小说。 \n' % (
            bookGroupingData['listSize'], bookGroupingData['listGroupSize'], bookGroupingData['listTaskSize']))
        self.logger.info('\t\t\t采集时间预算：共 %s 组，每组采集间隔 %s 秒，每组 %s 本小说，每本小说 预计 %s 秒，每组预计 %s 秒，总计 %s 秒 [ %s ]\n' % (
            bookGroupingData['listGroupSize'],
            self.b_second, bookGroupingData['listTaskSize'],
            self.b_second + 10,
            self.b_second + (self.b_second + 10) * bookGroupingData['listTaskSize'],
            (self.b_second + (bookGroupingData['listTaskSize']
                              * (self.b_second + 10))) * bookGroupingData['listGroupSize'],
            self.timeToo.changeTime(((self.b_second + (bookGroupingData['listTaskSize'] * (self.b_second + 10))))
                                    * bookGroupingData['listGroupSize'])))
        self.logger.info('========' * 15)
        self.setCatalogList(bookGroupingData)
        self.saveText()

        end = time.time()

        self.logger.info('---' * 30)
        self.logger.info('\t\t时间              ：%s' % (moment.now().format('YYYY-MM-DD HH:mm:ss')))
        self.logger.info('\t\t消耗 时间         ：%s 秒 [ %s ]' % (float(end) - float(start),
                                                             self.timeToo.changeTime(float(end) - float(start))))
        self.logger.info('\t\t采集 链接         : %s 条' % (self.countNum))
        self.logger.info('\t\t采集 失败链接     : %s 条' % (len(self.errorUrl)))
        self.logger.info('\t\t请求 失败链接     : %s 条' % (len(self.request404)))
        self.logger.info('\t\t采集 失败链接     ：\n\t\t\t' % (self.errorUrl))
        self.logger.info('\t\t请求 失败链接     ：\n\t\t\t' % (self.request404))
        # self.isOk()

    def contentsLoad(self):
        self.b_catalogList = []
        bookData = self.getBookData()
        if len(bookData) <= 0:
            self.logger.debug('bookTxtLoad 没有数据\n')
            return
        self.bookTxtLoad(bookData)

    def isOk(self):
        self.contentsLoad()


if __name__ == '__main__':
    getBookIdsListSize = input("获取多少组数据（最大10）: >>")
    maxCatalogNex = 1
    print(
        '\n\n参数确认： maxCatalogNex : %s | getBookIdsListSize : %s \n\n' % (maxCatalogNex, getBookIdsListSize))
    time.sleep(1)
    isStart = input("是否开始？(y/n): >>")
    if (isStart == 'y'):
        book = GetBookTXT(maxCatalogNex=maxCatalogNex, getBookIdsListSize=getBookIdsListSize)
        book.contentsLoad()
    else:
        print('取消抓取')
