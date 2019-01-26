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
import moment
import time

from GetBookInfoTool import GetBookInfoTool
from SaveBookInfoToMySqlTool import SaveBookInfoToMySqlToo
from public.MySqlTool import MySqlTool
from public.Logger import Logger
from public.DataTool import DataTool
from public.RedisTool import RedisTool


class GetBookTXT(object):
    def __init__(self, getBookIdsListSize, rdsKeyName):
        self.b_getBookIdsListSize = int(getBookIdsListSize)
        self.b_rdsKeyName = rdsKeyName
        self.b_title = 'getBookTXT'
        self.b_second = 1
        self.b_timeStr = moment.now().format('YYYY-MM-DD-HH-mm-ss')
        self.dataToo = DataTool(logName=self.b_title, second=self.b_second, timeStr=self.b_timeStr)
        self.mySql = MySqlTool(logName=self.dataToo.initLogName())
        self.logger = Logger(logname=self.dataToo.initLogName(), loglevel=1, logger=self.b_title).getlog()
        self.rds = RedisTool()
        self.getBookInfoToo = GetBookInfoTool(second=self.b_second, dataToo=self.dataToo, logger=self.logger)
        self.saveBookInfoToMySqlToo = SaveBookInfoToMySqlToo(second=self.b_second, logger=self.logger,
                                                             getBookInfoToo=self.getBookInfoToo,
                                                             mySql=self.mySql, dataToo=self.dataToo)

    def target(self):
        links = []
        for i in range(self.b_getBookIdsListSize):
            link = self.rds.r.lpop(self.b_rdsKeyName)
            if link != None:
                link = link.decode(encoding='utf-8')
                links.append(link)
        return links

    def contentsLoad(self):
        links = self.target()
        if len(links) <= 0:
            self.logger.debug('bookTxtLoad 没有数据\n')
            return
        for item in links:
            self.logger.debug(item)
            self.saveBookInfoToMySqlToo.saveText(link=item)
        self.isOk()

    def isOk(self):
        self.contentsLoad()


if __name__ == '__main__':
    rdsKeyName = 'bookIdsList3'
    getBookIdsListSize = input("每次获取多少条链接（最大1000）: >>")
    maxCatalogNex = 1
    print(
        '\n\n参数确认： rdsKeyName : %s | getBookIdsListSize : %s \n\n' % (rdsKeyName, getBookIdsListSize))
    time.sleep(1)
    isStart = input("是否开始？(y/n): >>")
    if (isStart == 'y'):
        book = GetBookTXT(getBookIdsListSize=getBookIdsListSize, rdsKeyName=rdsKeyName)
        book.contentsLoad()
    else:
        print('取消抓取')
