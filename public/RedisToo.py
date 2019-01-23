#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = 'Redis 操作'
__author__ = 'Mad Dragon'
__mtime__ = '2019/1/20'
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

import redis
import threading
from public.ConfigParser import ConfigParser
# 工具类简单，如果是字节，转成str
from redis import StrictRedis


def bytes_to_str(s, encoding='utf-8'):
    """Returns a str if a bytes object is given."""
    if isinstance(s, bytes):
        return s.decode(encoding)
    return s


class RedisToo():
    def __init__(self):
        self.con = ConfigParser()
        self.links = []
        self.pool = redis.ConnectionPool(host=self.con.getConfig('redisConfig', 'host'),
                                         port=self.con.getConfig('redisConfig', 'port'),
                                         db=self.con.getConfig('redisConfig', 'db'))
        self.r = redis.Redis(connection_pool=self.pool)
        self.p = redis.StrictRedis(connection_pool=self.pool)

    # 获取 并 删除 列表某些元素
    def getListData(self, name="list_name1", num=1):
        dataList = []
        for i in range(int(num)):
            data = self.r.lpop(name)
            if data != None:
                nData = bytes_to_str(data, 'utf-8')
                dataList.append(nData)

        return dataList

    # 批量添加列表
    def setListData(self, name='list_name1', lists=[]):
        if len(lists) <= 0:
            return False
        self.r.rpush(name, *lists)
        return True
