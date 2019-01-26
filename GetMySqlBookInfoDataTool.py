#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Mad Dragon'
__mtime__ = '2019/1/24'
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


class GetMySqlBookInfoDataToo():
    def __init__(self, mySql, dataToo, logger):
        self.mySql = mySql
        self.dataToo = dataToo
        self.logger = logger

    def getBookIdData(self, nex=0, limit='', data=[]):
        sqlStr = "select book_Id from books where 1=1"
        if len(str(nex)):
            sqlStr = '%s and nex > %s' % (sqlStr, nex)
        if len(str(limit)):
            sqlStr = '%s and limit %s' % (sqlStr, limit)
        if len(data):
            sqlStr = '%s and book_Id in  %s' % (sqlStr, self.dataToo.listToStr(data))

        bookData = self.mySql.getListData(sqlStr=sqlStr)
        bookId = []
        for item in bookData:
            bookId.append(item[0])
        self.logger.info("[ GetMySqlBookInfoDataToo - getBookId ]: 获取书籍 [ %s ] 本 \n %s" % (len(bookId), bookId))
        return bookId

    def getBookId(self, environmentalType=0, testBookId=['10000611804961003', '10000828104982003'], nex=0,
                  limit='10000,20000'):
        if environmentalType == 2:
            bookId = self.getBookIdData(nex=nex)
        elif environmentalType == 1:
            bookId = self.getBookIdData(nex=nex, limit=limit)
        else:
            bookId = self.getBookIdData(data=testBookId)
        return bookId

    def getLinksUrlData(self, data=[], fs=0, nex=1):
        sqlStr = "select url from links where 1 = 1"
        if len(str(fs)):
            sqlStr = '%s and fs = %s' % (sqlStr, fs)
        if len(str(nex)):
            sqlStr = '%s and nex < %s' % (sqlStr, nex)
        if len(data):
            sqlStr = '%s and book_Id in %s ' % (sqlStr, self.dataToo.listToStr(data))

        urlData = self.mySql.getListData(sqlStr=sqlStr)
        links = []
        for item in urlData:
            links.append(item[0])
        self.logger.info("[ GetMySqlBookInfoDataToo - getLinksUrl ]: 获取链接 [ %s ] 条 \n %s" % (len(links), links))
        return links

    def getLinksUrl(self, environmentalType=0, data=['10000611804961003', '10000828104982003'], nex=1,
                    fs=0):
        if environmentalType == 2:
            links = self.getLinksUrlData(nex=nex, fs=fs, data=data)
        elif environmentalType == 1:
            links = self.getLinksUrlData(nex=nex, fs=fs, data=data)
        else:
            links = self.getLinksUrlData(nex=100, fs=fs, data=data)
        return links
