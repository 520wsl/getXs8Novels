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
import datetime
import time

import moment
from lxml import etree

from public.ConfigParser import ConfigParser
from public.DataToo import DataToo
from public.Logger import Logger


class GetFreeBookTXT():
    def __init__(self):
        self.b_title = 'GetFreeBookTXT'
        self.b_second = 1
        self.b_timeStr = moment.now().format('YYYY-MM-DD-HH-mm-ss')

        self.errorUrl = []
        self.request404 = []
        self.bookInfoList = []
        self.countNum = 0

        self.con = ConfigParser()
        self.freeBookListPage = self.con.getConfig('webConfig', 'freeBookListPage')
        self.dataToo = DataToo(logName=self.b_title, second=self.b_second, timeStr=self.b_timeStr)
        self.logger = Logger(logname=self.dataToo.initLogName(), loglevel=1, logger=self.b_title).getlog()

    def getBookList(self):
        link = self.freeBookListPage

        text = self.dataToo.getText(link=link)
        if len(text['data']) <= 0:
            self.errorUrl.append(link)
            self.countNum += 1
            self.logger.debug('第 %s 条链接：数据抓取异常 ：%s\n' % (self.countNum, text))
            return
        html = etree.HTML(text['data'])
        content_list = html.xpath('//*[@id="limit-list"]/div/ul/li')

        if len(content_list) <= 0:
            self.countNum += 1
            title = html.xpath('//title/text()')
            requestIntercept = html.xpath('//div[@class="empty-text"]//strong/text()')
            request404 = html.xpath('//h3[@class="lang"]/text()')
            self.logger.debug('第 %s 条链接：HTML解析异常！' % (self.countNum))
            self.logger.debug('第 %s 条链接[title]：%s' % (self.countNum, title))
            if len(requestIntercept) > 0:
                self.errorUrl.append(link)
                second = self.b_second * 180
                self.logger.debug('第 %s 条链接[requestIntercept]：%s 被拦截了暂停 %s 秒后 抓取下一条链接 '
                                  % (self.countNum, requestIntercept, second))
                time.sleep(second)
            if len(request404) > 0:
                self.request404.append(link)
                self.logger.debug('第 %s 条链接[request404]：%s' % (self.countNum, request404))
            self.logger.debug('第 %s 条链接[text]：%s\n' % (self.countNum, text))
            return
        bookInfoList = []
        for item in content_list:
            book_Id = item.xpath('.//div[@class="book-mid-info"]/h4/a/@href')[0][6:]
            book_name = item.xpath('.//div[@class="book-mid-info"]/h4/a/text()')[0]
            author = item.xpath('.//p[@class="author"]/a[contains(concat("",@class,"name"),"")]/text()')[0]
            chan_name = item.xpath('.//p[@class="author"]/a[2]/text()')[0]
            state = item.xpath('.//p[@class="author"]/span/text()')[0]
            img_url = item.xpath('.//div[@class="book-img-box"]/a/img/@src')[0]
            synopticHtml = item.xpath('.//div[@class="book-mid-info"]//p[@class="intro"]')[0]
            synoptic = etree.tostring(synopticHtml, method='xml').decode('utf-8')
            self.logger.debug(book_Id)
            self.logger.debug(book_name)
            self.logger.debug(author)
            self.logger.debug(chan_name)
            self.logger.debug(state)
            self.logger.debug(img_url)
            self.logger.debug(synoptic)
            bookInfoList.append({
                'book_Id': book_Id,
                'book_name': book_name,
                'author': author,
                'chan_name': chan_name,
                'state': state,
                'img_url': img_url,
                'synoptic': synoptic

            })
        self.logger.info('免费书籍信息采集完成：%s' % (bookInfoList))
        return bookInfoList

    # 链接处理
    def linkLoad(self, bookId):
        day = datetime.now()
        unix = datetime.timestamp(day)
        return self.con.getConfig('webConfig', 'host') + '/ajax/chapter/userChapterList?_csrfToken=&bookId=' + str(
            bookId) + '&_=' + str(
            int(unix))

    def getBookCatalogInfo(self, bookId):
        link = self.linkLoad(bookId)

        jsonData = self.dataToo.getJson(link=link)
        if len(jsonData['data']) <= 0:
            self.errorUrl.append(link)
            self.countNum += 1
            self.logger.debug('第 %s 条链接：数据抓取异常 ：%s\n' % (self.countNum, jsonData))
            return
        bookInfo = {}
        bookInfo['bookId'] = jsonData['data']['bookId']
        bookInfo['bookName'] = jsonData['data']['bookName']
        bookInfo['chapterTotalCnt'] = jsonData['data']['chapterTotalCnt']
        bookInfo['catalog'] = jsonData['data']['vs']

        # html = etree.HTML(text['data'])
        # content_list = html.xpath('//*[@id="limit-list"]/div/ul/li')
        #
        # if len(content_list) <= 0:
        #     self.countNum += 1
        #     title = html.xpath('//title/text()')
        #     requestIntercept = html.xpath('//div[@class="empty-text"]//strong/text()')
        #     request404 = html.xpath('//h3[@class="lang"]/text()')
        #     self.logger.debug('第 %s 条链接：HTML解析异常！' % (self.countNum))
        #     self.logger.debug('第 %s 条链接[title]：%s' % (self.countNum, title))
        #     if len(requestIntercept) > 0:
        #         self.errorUrl.append(link)
        #         second = self.b_second * 180
        #         self.logger.debug('第 %s 条链接[requestIntercept]：%s 被拦截了暂停 %s 秒后 抓取下一条链接 '
        #                           % (self.countNum, requestIntercept, second))
        #         time.sleep(second)
        #     if len(request404) > 0:
        #         self.request404.append(link)
        #         self.logger.debug('第 %s 条链接[request404]：%s' % (self.countNum, request404))
        #     self.logger.debug('第 %s 条链接[text]：%s\n' % (self.countNum, text))
        #     return
        # bookInfoList = []
        # for item in content_list:
        #     book_Id = item.xpath('.//div[@class="book-mid-info"]/h4/a/@href')[0][6:]
        #     book_name = item.xpath('.//div[@class="book-mid-info"]/h4/a/text()')[0]
        #     author = item.xpath('.//p[@class="author"]/a[contains(concat("",@class,"name"),"")]/text()')[0]
        #     chan_name = item.xpath('.//p[@class="author"]/a[2]/text()')[0]
        #     state = item.xpath('.//p[@class="author"]/span/text()')[0]
        #     img_url = item.xpath('.//div[@class="book-img-box"]/a/img/@src')[0]
        #     synopticHtml = item.xpath('.//div[@class="book-mid-info"]//p[@class="intro"]')[0]
        #     synoptic = etree.tostring(synopticHtml, method='xml').decode('utf-8')
        #     self.logger.debug(book_Id)
        #     self.logger.debug(book_name)
        #     self.logger.debug(author)
        #     self.logger.debug(chan_name)
        #     self.logger.debug(state)
        #     self.logger.debug(img_url)
        #     self.logger.debug(synoptic)
        #     bookInfoList.append({
        #         'book_Id': book_Id,
        #         'book_name': book_name,
        #         'author': author,
        #         'chan_name': chan_name,
        #         'state': state,
        #         'img_url': img_url,
        #         'synoptic': synoptic
        #
        #     })
        # self.logger.info('免费书籍信息采集完成：%s' % (bookInfoList))
        # return bookInfoList


if __name__ == '__main__':
    getFreeBookTXT = GetFreeBookTXT()
    getFreeBookTXT.getBookList()
    pass
