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

from tool.GetMySqlBookInfoDataTool import GetMySqlBookInfoDataToo
from public.DataTool import DataTool
from public.Logger import Logger
from public.MySqlTool import MySqlTool
from public.RedisTool import RedisTool


class SaveBookToRedisTool():
    def __init__(self, environmentalType, rds, dataToo, mySql, logger):
        self.b_bookPageSize = 100
        self.b_fs = 0
        self.b_maxCatalogNex = 1
        self.b_environmentalType = int(environmentalType)
        self.b_title = 'SaveBookToRedis'
        self.b_second = 1
        self.b_timeStr = moment.now().format('YYYY-MM-DD-HH-mm-ss')

        self.rds = rds
        self.dataToo = dataToo
        self.mySql = mySql
        self.logger = logger
        self.getMySqlBookInfoDataToo = GetMySqlBookInfoDataToo(mySql=self.mySql, dataToo=self.dataToo,
                                                               logger=self.logger)

    def saveBookListToRedis(self, bookId, rdsKeyName):
        if len(bookId) <= 0:
            self.logger.debug('saveBookListToRedis 没有数据\n')
            return
        linkCount = 0
        bookGroupingData = self.dataToo.groupingData(list=bookId, pageSize=self.b_bookPageSize)
        for item in bookGroupingData['listTaskList']:
            time.sleep(self.b_second)
            self.logger.debug("%s\n" % item)
            catalogData = self.getMySqlBookInfoDataToo.getLinksUrl(environmentalType=self.b_environmentalType,
                                                                   data=item, fs=self.b_fs, nex=self.b_maxCatalogNex)
            linkCount += len(catalogData)
            self.rds.setListData(rdsKeyName=rdsKeyName, lists=self.dataToo.getLinkArr(catalogData))

        self.logger.info('数据处理完成，存储书籍 [ %s ] 本, 共 [ %s ] 个章节' % (len(bookId), linkCount))

    def saveAllBookListToRedis(self, rdsKeyName):
        bookId = self.getMySqlBookInfoDataToo.getBookId(environmentalType=self.b_environmentalType)
        self.saveBookListToRedis(bookId=bookId, rdsKeyName=rdsKeyName)


if __name__ == '__main__':
    b_title = 'SaveBookToRedisTool'
    b_second = 1
    b_timeStr = moment.now().format('YYYY-MM-DD-HH-mm-ss')
    rds = RedisTool()
    dataToo = DataTool(logName=b_title, second=b_second, timeStr=b_timeStr)
    logger = Logger(logname=dataToo.initLogName(), loglevel=1, logger=b_title).getlog()
    mySql = MySqlTool(logName=dataToo.initLogName())

    rdsKeyName = 'bookIdsList3'

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
        book = SaveBookToRedisTool(environmentalType=environmentalType, rds=rds, dataToo=dataToo, mySql=mySql,
                                   logger=logger)
        book.saveAllBookListToRedis(rdsKeyName=rdsKeyName)
    else:
        print('取消抓取')
