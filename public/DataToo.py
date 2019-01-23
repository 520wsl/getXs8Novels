#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = '数据处理'
__author__ = 'Mad Dragon'
__mtime__ = '2019/1/16'
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
import math
import random
import threading
import time

import requests

from public.Logger import Logger


class DataToo():
    def __init__(self, logName, second):
        self.b_second = second
        self.logger = Logger(logname=logName, loglevel=1, logger="DataToo").getlog()

    def groupingData(self, list, pageSize, fixed=False):
        listSize = len(list)
        if fixed:
            listGroupSize = pageSize
        else:
            listGroupSize = math.ceil(float(listSize) / pageSize)

        nloops = range(listGroupSize)
        listTaskList = []
        listTaskSize = math.ceil(float(listSize) / listGroupSize)
        for i in nloops:
            try:
                self.logger.info("第 %s 组 ：[ %s ] \n\t" % (i + 1, len(list[i * listTaskSize:(i + 1) * listTaskSize])))
                listTaskList.append(list[i * listTaskSize:(i + 1) * listTaskSize])
            except:
                self.logger.info("第 %s 组 ：[ %s ] \n\t" % (i + 1, len(list[i * listTaskSize:])))
                listTaskList.append(list[i * listTaskSize:])
        res = {
            'listSize': listSize,
            'listGroupSize': listGroupSize,
            'listTaskSize': listTaskSize,
            'listTaskList': listTaskList
        }
        self.logger.info('groupingData : %s' % res)
        return res

    def threads(self, taskList, target):
        nloops = range(len(taskList))
        # self.logger.debug('threads:==>\n\t %s \n\t %s' % (nloops, taskList))

        threads = []
        for i in nloops:
            if len(taskList[i]) <= 0: continue
            t = threading.Thread(target=target, args=(taskList[i], i))
            threads.append(t)

        for i in nloops:
            if len(taskList[i]) <= 0: continue
            threads[i].start()

        for i in nloops:
            if len(taskList[i]) <= 0: continue
            threads[i].join()

        # 调接口获取数据

    def getHTMLTxt(self, link, heads):
        result = {'status': '200', 'data': '', 'link': link}

        # r = requests.get(link, headers=heads)
        # r.encoding = "utr-8"
        #
        # result['data'] = r.text
        # return result

        try:
            r = requests.get(link, headers=heads, timeout=10)
            r.encoding = "utr-8"
            result['data'] = r.text
        except:
            second = random.randint(0, self.b_second * 60)
            self.logger.debug('[ %s ][ 403 ] 可能被拦截了暂停 %s 秒后 抓取下一条链接 !\n' % (link, second))
            time.sleep(second)
            result['status'] = '403'
        return result

    def listToStr(self, data_info):
        # links = ','.join(data_info)
        return tuple(data_info)
        # for item in links:
            # print(item)
            # print(str(item))

        # return str(','.join(data_info))

    def getText(self, link, heads):
        if len(link) <= 0: return
        return self.getHTMLTxt(link=link, heads=heads)
