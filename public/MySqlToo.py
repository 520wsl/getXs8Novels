#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = 'mysql操作处理'
__author__ = 'Mad Dragon'
__mtime__ = '2019/1/15'
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
import pymysql
from public.Logger import Logger
from public.ConfigParser import ConfigParser


class MySqlToo():
    def __init__(self, logName):
        self.con = ConfigParser()
        self.logger = Logger(logname=logName, loglevel=1, logger="MySQLToo").getlog()
        mysqlConfig = self.con.getConfig('mysql', 'host'), self.con.getConfig('mysql', 'user'), self.con.getConfig(
            'mysql', 'password'), self.con.getConfig('mysql', 'database')
        self.logger.info(
        "\n\t mySqlConfig:\n\t\t host: %s\n\t\t user : %s\n\t\t password : %s\n\t\t database : %s " % (mysqlConfig))
    # 数据库信息
    def openMySqlConfig(self):
        return pymysql.connect(self.con.getConfig('mysql', 'host'), self.con.getConfig('mysql', 'user'), self.con.getConfig(
            'mysql', 'password'), self.con.getConfig('mysql', 'database'))
        # 批量添加 信息

        # 批量添加 信息

    def batchAdd(self, sql, data_info):
        # self.logger.warning(data_info)
        db = self.openMySqlConfig()
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()

        try:
            # 执行sql语句
            cursor.executemany(sql, data_info)
            # 提交到数据库执行
            db.commit()
            db.close()
            self.logger.info('存储成功')
            return True
        except:
            # 如果发生错误则回滚
            db.rollback()
            db.close()
            self.logger.debug('存储失败：[ sql ] %s ' % (str(sql)))
            self.logger.debug('存储失败：[ data_info ] %s ' % (str(data_info)))
            return False

    # 获取列表数据
    def getListData(self, sql):
        db = self.openMySqlConfig()
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()
        results = []

        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
            db.close()
            self.logger.debug("查询成功[ %s ]: sql==> %s" % (len(results), sql))
            return results
        except:
            self.logger.debug("查询失败: sql==> %s" % (sql))
            # 关闭数据库连接
            db.close()
            return results
