#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = '免费文章抓取'
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

from public.ConfigParser import ConfigParser
from tool.GetBookInfoTool import GetBookInfoTool
from tool.SaveBookInfoToMySqlTool import SaveBookInfoToMySqlToo
from public.MySqlTool import MySqlTool
from public.Logger import Logger
from public.DataTool import DataTool
from public.RedisTool import RedisTool


class getFreeBookTXT(object):
    def __init__(self):
        # self.b_getBookIdsListSize = int(getBookIdsListSize)
        # self.b_rdsKeyName = rdsKeyName
        self.b_title = 'getFreeBookTXT'
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
        self.con = ConfigParser()

    def getFreeBookLink(self):
        bookInfoList = self.getBookInfoToo.toFreeBookListPageGetBookList(
            freeBookListPage=self.con.getConfig('webConfig', 'freeBookListPage'))
        self.logger.debug(bookInfoList)
        return bookInfoList

    # def target(self):
    #     # links = []
    # for i in range(self.b_getBookIdsListSize):
    #     link = self.rds.r.lpop(self.b_rdsKeyName)
    #     if link != None:
    #         link = link.decode(encoding='utf-8')
    #         links.append(link)
    # return links
    def formatCatalogInfo(self, data):
        catalogData = data['vs']
        links = []
        for i in catalogData:
            for j in i['cs']:
                url = self.con.getConfig('webConfig', 'host') + '/chapter/' + data['bookId']+ '/' + j['id']
                # links.append({j['id'], j['cN'], bookId, bookName, j['cnt'], url, j['uuid'], j['fS']})
                # links.append(str(url))
                self.saveBookInfoToMySqlToo.saveText(link=str(url))
        return links

    def contentsLoad(self):
        links = self.getFreeBookLink()
        if len(links) <= 0:
            self.logger.debug('getFreeBookLink 没有数据\n')
            return
        for item in links:
            # self.logger.debug(item)
            # self.logger.debug(item['book_Id'])
            time.sleep(self.b_second)
            jsonData = self.getBookInfoToo.getCatalogInfo(bookId=item['book_Id'])
            self.logger.debug(jsonData)
            catalogData = self.formatCatalogInfo(data=jsonData['data'])
            self.logger.debug(catalogData)
            self.saveBookInfoToMySqlToo.saveCatalog(bookId=jsonData['data']['bookId'])
        # self.isOk()
    #
    # def isOk(self):
    #     self.contentsLoad()


if __name__ == '__main__':
    g = getFreeBookTXT()
    g.contentsLoad()
    # rdsKeyName = 'bookIdsList3'
    # getBookIdsListSize = input("每次获取多少条链接（最大1000）: >>")
    # maxCatalogNex = 1
    # print(
    #     '\n\n参数确认： rdsKeyName : %s | getBookIdsListSize : %s \n\n' % (rdsKeyName, getBookIdsListSize))
    # time.sleep(1)
    # isStart = input("是否开始？(y/n): >>")
    # if (isStart == 'y'):
    #     book = getFreeBookTXT(getBookIdsListSize=getBookIdsListSize, rdsKeyName=rdsKeyName)
    #     book.contentsLoad()
    # else:
    #     print('取消抓取')
