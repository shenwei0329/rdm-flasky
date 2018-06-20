#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
#
#   个人档案
#   =-=-=-=-
#   基于个人的信息集合
#

import mongodb_class
import handler
import logging
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class Member:

    def __init__(self, name):
        self.name = name
        self.task = []
        self.work_log = []
        self.quota = 0.
        self.ind = None
        self.mongodb = mongodb_class.mongoDB()

    def get_name(self):
        return self.name

    def add_task(self, task):
        if task in self.task:
            return
        for _t in self.task:
            if _t['issue'] == task['issue']:
                _idx = self.task.insert(_t)
                self.task[_idx] = task
                return
        self.task.append(task)

    def add_work_log(self, work_log):
        if work_log in self.work_log:
            return
        self.work_log.append(work_log)

    def get_task(self):
        return self.task

    def get_work_log(self):
        return self.work_log

    def get_task_count(self):
        return len(self.task)

    def get_work_log_count(self):
        return len(self.work_log)

    def cal_quota(self, st_date, ed_date):

        _quota = 0.

        for _i in self.task:

            _issue_updated_date = _i["updated"].split('T')[0]
            if handler.isDateBef(_issue_updated_date, st_date) or handler.isDateAft(_issue_updated_date, ed_date):
                continue

            if u'完成' not in _i['status']:
                continue
            if (_i['org_time'] is None) and (_i['spent_time'] is None):
                continue
            if _i['org_time'] is None:
                _org_time = float(_i['spent_time'])
                _spent_time = float(_i['spent_time'])
            elif _i['spent_time'] is None:
                _org_time = float(_i['org_time'])
                _spent_time = float(_i['org_time'])
            else:
                _org_time = float(_i['org_time'])
                _spent_time = float(_i['spent_time'])
            if _spent_time == 0:
                _quota += _org_time
            else:
                _miu = _org_time / _spent_time
                if _miu > 10:  # 预估时间严重失真
                    _miu = 1.8
                elif _miu > 5:  # 预估时间偏离过大
                    _miu = 1.5
                elif _miu > 1:  # 经验问题
                    _miu = 1.3
                _quota += (_org_time * _miu)
        self.quota = _quota

    def get_quota(self):
        return self.quota

    def cal_ind(self, st_date, ed_date):

        _doing = 0
        _done = 0
        _spent_doing = 0
        _spent_done = 0
        _ind = {}
        for _i in self.task:

            _issue_updated_date = _i["updated"].split('T')[0]
            if handler.isDateBef(_issue_updated_date, st_date) or handler.isDateAft(_issue_updated_date, ed_date):
                continue

            if _i['org_time'] is not None:
                if u'完成' not in _i['status']:
                    _doing += _i['org_time']
                else:
                    _done += _i['org_time']

            if _i['spent_time'] is not None:
                if u'完成' not in _i['status']:
                    _spent_doing += _i['spent_time']
                else:
                    _spent_done += _i['spent_time']

        _ind['doing'] = _doing / 3600
        _ind['done'] = _done / 3600
        _ind['spent_doing'] = _spent_doing / 3600
        _ind['spent_done'] = _spent_done / 3600

        self.ind = _ind

    def get_ind(self):
        return self.ind
