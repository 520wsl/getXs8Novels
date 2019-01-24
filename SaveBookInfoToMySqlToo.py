#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = '书籍数据存储工具类'
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
import time

import moment

from GetBookInfoToo import GetBookInfoToo
from public.DataToo import DataToo
from public.Logger import Logger
from public.MySqlToo import MySqlToo


class SaveBookInfoToMySqlToo():
    def __init__(self, second, logger, getBookInfoToo, mySql, dataToo):
        self.b_second = second
        self.b_fs = 0
        self.b_maxCatalogNex = 0

        self.m_saveText = "INSERT INTO `links` (`url`,article) VALUES (%s, %s) ON DUPLICATE KEY UPDATE article = VALUES (article), nex = nex+1"

        self.m_getCatalogData = "SELECT url FROM links WHERE fs = %s  AND nex < %s AND book_Id in " % (
            self.b_fs, self.b_maxCatalogNex)

        self.getBookInfoToo = getBookInfoToo
        self.dataToo = dataToo
        self.mySql = mySql
        self.logger = logger

    def saveText(self, link):
        time.sleep(self.b_second)
        content = self.getBookInfoToo.getTxtInfo(link)
        if len(content) <= 0: return False
        self.logger.debug('书籍 [ %s ] 文章存储' % (link))
        return self.mySql.batchAdd(sql=self.m_saveText, data_info=[(link, content)])


if __name__ == '__main__':
    b_title = 'GetBookInfoToo'
    b_second = 1
    b_timeStr = moment.now().format('YYYY-MM-DD-HH-mm-ss')
    dataToo = DataToo(logName=b_title, second=b_second, timeStr=b_timeStr)
    logger = Logger(logname=dataToo.initLogName(), loglevel=1, logger=b_title).getlog()
    mySql = MySqlToo(logName=dataToo.initLogName())
    getBookInfoToo = GetBookInfoToo(second=b_second, dataToo=dataToo, logger=logger)
    saveBookInfoToMySqlToo = SaveBookInfoToMySqlToo(second=b_second, logger=logger,
                                                    getBookInfoToo=getBookInfoToo,
                                                    mySql=mySql, dataToo=dataToo)
