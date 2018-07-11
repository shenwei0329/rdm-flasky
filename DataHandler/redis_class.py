#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
#
# 数据缓存管理
# ============
#
#

import sys
import redis
import pickle
import datetime

import logging

reload(sys)
sys.setdefaultencoding('utf-8')


class RedisClass:
    """
    Redis处理类
    """

    def __init__(self, host='127.0.0.1', port=6379, db=10):
        self.r = redis.Redis(host=host, port=port, db=db)

    def set(self, key, value):
        self.r.set('rdms.'+key, pickle.dumps(value))
        self.r.set('rdms.timestamp.'+key, pickle.dumps(datetime.datetime.now()))

    def get(self, key):
        return pickle.loads(self.r.get('rdms.'+key))

    def get_time_stamp(self, key):
        return pickle.loads(self.r.get('rdms.timestamp.'+key))

    def exists(self, name):
        return self.r.exists('rdms.'+name)


class KeyLiveClass:
    """
    键值管理类
    """

    def __init__(self, key):
        self.key = key
        if myRedis.exists(key):
            self.value = myRedis.get(key)

    def set(self, value):
        myRedis.set(self.key, value)

    def alive(self, seconds):

        if not myRedis.exists(self.key):
            return False

        _time_stamp = myRedis.get_time_stamp(self.key)
        if (datetime.datetime.now() - _time_stamp).seconds > seconds:
            return False
        return True

    def get(self):
        return myRedis.get(self.key)


# 针对公司公共的Redis服务
myRedis = RedisClass(host='172.16.60.2')
