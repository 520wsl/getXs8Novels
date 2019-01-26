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
import time
import moment
from lxml import etree
from datetime import datetime
from public.ConfigParser import ConfigParser
from public.DataTool import DataTool
from public.Logger import Logger


class GetBookInfoTool():
    def __init__(self, second, dataToo, logger):
        self.b_second = second

        self.errorUrl = []
        self.request404 = []
        self.bookInfoList = []
        self.bookCountNum = 0
        self.freeBookCountNum = 0
        self.bookCatalogCountNum = 0
        self.bookTxtCountNum = 0

        self.con = ConfigParser()
        self.dataToo = dataToo
        self.logger = logger

    def exceptions(self, html, link, text):
        title = html.xpath('//title/text()')
        requestIntercept = html.xpath('//div[@class="empty-text"]//strong/text()')
        request404 = html.xpath('//h3[@class="lang"]/text()')
        requestNode = html.xpath('//div[@class="no-data"]/h3/text()')
        self.logger.debug('链接 [ %s ] ：HTML解析异常！' % (link))
        self.logger.debug('[title]：%s' % (title))

        if len(requestIntercept) > 0:
            self.errorUrl.append(link)
            second = self.b_second * 180
            self.logger.debug('[requestIntercept]：%s 被拦截了暂停 %s 秒后 抓取下一条链接 '
                              % (requestIntercept, second))
            time.sleep(second)

        if len(requestNode) > 0:
            self.errorUrl.append(link)
            self.logger.debug('[requestNode]：%s' % (requestNode))

        if len(request404) > 0:
            self.request404.append(link)
            self.logger.debug('[request404]：%s' % (request404))

        self.logger.debug('[text]：%s\n' % (text))

    def noData(self, link, text):
        self.errorUrl.append(link)
        self.logger.debug('链接 [ %s ] ：数据抓取异常 ：%s\n' % (link, text))

    def getContentList(self, link, xpath):
        contentList = []
        text = self.dataToo.getText(link=link)
        if len(text['data']) <= 0:
            self.noData(link, text)
            return contentList
        html = etree.HTML(text['data'])
        contentList = html.xpath(xpath)
        if len(contentList) <= 0:
            self.exceptions(html, link, text)
        return contentList

    # 去书籍搜索列表获取书籍列表
    def toAllBookListPageGetBookList(self, link):
        time.sleep(self.b_second)
        content_list = self.getContentList(link=link, xpath='//div[@class="right-book-list"]//li')
        if len(content_list) <= 0:
            self.bookCountNum += 1
            return
        bookInfoList = []
        for item in content_list:
            book_Id = item.xpath('.//div[@class="book-info"]/h3/a/@href')[0][6:]
            book_name = item.xpath('.//div[@class="book-info"]/h3/a/text()')[0]
            author = item.xpath('.//div[@class="book-info"]/h4/a/text()')[0]
            tag = item.xpath('.//div[@class="book-info"]/p[@class="tag"]/span/text()')
            synoptic = item.xpath('.//div[@class="book-info"]/p[@class="intro"]/text()')[0]
            img_url = item.xpath('.//div[@class="book-img"]/a/img/@src')[0]
            chan_name = tag[0]
            state = tag[1]
            bookInfoList.append({
                'book_Id': book_Id,
                'book_name': book_name,
                'state': state,
                'author': author,
                'chan_name': chan_name,
                'synoptic': str(synoptic),
                'img_url': img_url
            })
        self.logger.info('书籍列 [ %s ] 表信息采集完成：%s' % (link, bookInfoList))
        self.freeBookCountNum += 1
        return bookInfoList

    # 去免费书籍页面获取书籍列表
    def toFreeBookListPageGetBookList(self, freeBookListPage):
        link = freeBookListPage
        content_list = self.getContentList(link=link, xpath='//*[@id="limit-list"]/div/ul/li')
        if len(content_list) <= 0:
            self.freeBookCountNum += 1
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
            bookInfoList.append({
                'book_Id': book_Id,
                'book_name': book_name,
                'author': author,
                'chan_name': chan_name,
                'state': state,
                'img_url': img_url,
                'synoptic': synoptic

            })
        self.logger.info('免费书籍列表【 %s 】信息采集完成：%s' % (link, bookInfoList))
        self.freeBookCountNum += 1
        return bookInfoList

    # 链接处理
    def bookLinkLoad(self, bookId):
        day = datetime.now()
        unix = datetime.timestamp(day)
        return self.con.getConfig('webConfig', 'host') + '/ajax/chapter/userChapterList?_csrfToken=&bookId=' + str(
            bookId) + '&_=' + str(
            int(unix))

    def getCatalogInfo(self, bookId):
        link = self.bookLinkLoad(bookId)
        time.sleep(self.b_second)
        jsonData = self.dataToo.getJson(link=link)
        if len(jsonData['data']['data']) <= 0:
            self.bookCatalogCountNum += 1
            self.noData(link, jsonData)
            return

        self.logger.info('书籍【 %s 】目录信息采集完成：%s' % (link, jsonData['data']))
        self.bookCatalogCountNum += 1
        return jsonData['data']

    def getTxtInfo(self, link):
        content = ''
        time.sleep(self.b_second)
        content_list = self.getContentList(link=link, xpath='//div[@class="read-content j_readContent"]')
        if len(content_list) <= 0:
            self.freeBookCountNum += 1
            return content
        content_list = content_list[0]
        content = etree.tostring(content_list, method='xml').decode('utf-8')
        self.logger.info('书籍【 %s 】章节信息采集完成' % (link))
        self.bookTxtCountNum += 1
        return content


if __name__ == '__main__':
    b_title = 'GetBookInfoToo'
    b_second = 1
    b_timeStr = moment.now().format('YYYY-MM-DD-HH-mm-ss')
    dataToo = DataTool(logName=b_title, second=b_second, timeStr=b_timeStr)
    logger = Logger(logname=dataToo.initLogName(), loglevel=1, logger=b_title).getlog()
    b = GetBookInfoTool(second=b_second, dataToo=dataToo, logger=logger)
    msg = [
        ('0、[ toAllBookListPageGetBookList ] 小说列表页抓取',
         "[ paramsCase ]: ",
         "https://www.xs8.cn/all?pageSize=500&gender=2&catId=-1&isFinish=-1&isVip=-1&size=-1&updT=-1&orderBy=0&pageNum=1"),
        ('1、[ toFreeBookListPageGetBookList ] 免费小说列表页抓取',
         "[ paramsCase ]: ", b.con.getConfig('webConfig', 'freeBookListPage')),
        ('2、[ getCatalogInfo ] 小说章节目录抓取', "[ paramsCase ]: ", "12388396604821403"),
        ('3、[ getTxtInfo ] 小说文章抓取',
         "[ paramsCase ]: ", "https://www.xs8.cn/chapter/12388396604821403/34416289199831222")
    ]

    b.logger.info('页面类型:')
    for item in msg:
        b.logger.info('\t%s' % item[0])

    time.sleep(1)
    actionType = int(input('请选择要抓取的页面类型: >>'))
    b.logger.info('您选择的是: %s ' % actionType)
    b.logger.info(msg[actionType][0])
    b.logger.info('%s %s' % (msg[actionType][1], msg[actionType][2]))
    time.sleep(1)
    params = str(input('请参考 [ paramsCase ] 填写参数: >>'))
    if len(params) <= 0:
        params = msg[actionType][2]
    b.logger.info("params : %s" % params)
    time.sleep(1)
    isStart = input("是否开始？(y/n): >>")
    if (isStart == 'y'):
        if actionType == 0:
            b.toAllBookListPageGetBookList(params)
        elif actionType == 1:
            b.toFreeBookListPageGetBookList(params)
        elif actionType == 2:
            b.getCatalogInfo(params)
        elif actionType == 3:
            b.getTxtInfo(params)
    else:
        print('取消抓取')
