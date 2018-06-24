#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
#
#   个人档案
#   =-=-=-=-
#   基于个人的信息集合
#
#   个人档案
#   =======
#   研发管理的两个最基本元素：人（注：仅针对产品研发、项目开发和测试）、事
#   通过个人档案建立以人为主题的数据集，实现“事”的聚集，并通过人与事之间的不同维度的数据分析建立个人最核心的价值描述。
#   目前的数据：
#       -）基本信息：姓名、邮箱、职级、岗位、归属部门
#       -）任务与执行：当前任务分配的饱满程度、执行情况、偏向产品研发或项目开发
#       -）工作日志：可衡量出1个spent_time对应了多少个work_hour，简介说明任务的"难度"
#       -）考勤：出勤情况
#       -）差旅：差旅情况
#
#   个人有哪些特征？
#   如何有效评价？
#

import mongodb_class
import handler
import logging
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class Member:

    def __init__(self, name, dpt):
        """
        初始化
        :param name: 姓名
        :param dpt: 部门
        """
        self.name = name
        self.dpt = dpt
        self.task = []
        self.work_log = []
        self.quota = 0.
        self.plan_quota = 0.
        self.ext_quota = 0.
        self.ext_plan_quota = 0.
        self.ind = None
        self.mongodb = mongodb_class.mongoDB()
        self.email = self._get_email()
        logging.log(logging.WARN, u">>> Member.__init__(%s,%s,%s)" % (self.name, self.dpt, self.email))

    def _get_email(self):
        """
        获取个人的邮箱
        :return:
        """
        _search = {u'用户姓名': self.name, u'所属部门': self.dpt}
        self.mongodb.connect_db('ext_system')
        _email = self.mongodb.handler('member_email_t', 'find_one', _search)
        if _email is not None:
            return _email[u'邮箱地址']
        return None

    def get_name(self):
        """
        获取个人姓名
        :return: 姓名
        """
        return self.name

    def add_task(self, task):
        """
        添加任务
        :param task: 任务（是Issue内容的子集）
        :return:
        """
        if task in self.task:
            return
        for _t in self.task:
            if _t['issue'] == task['issue']:
                """取代已有数据"""
                _idx = self.task.index(_t)
                self.task[_idx] = task
                return
        self.task.append(task)

    def add_work_log(self, work_log):
        """
        添加工作日志
        :param work_log: 工作日志
        :return:
        """
        if work_log in self.work_log:
            return
        self.work_log.append(work_log)

    def get_task(self):
        """
        获取个人的任务集
        :return: 任务集
        """
        return self.task

    def get_work_log(self):
        """
        获取个人的工作日志集
        :return: 数据集
        """
        return self.work_log

    def get_task_count(self):
        """
        获取个人的任务总数
        :return: 总数
        """
        return len(self.task)

    def get_work_log_count(self):
        """
        获取个人的工作日志总数
        :return: 总数
        """
        return len(self.work_log)

    def cal_plan_quota(self, st_date, ed_date):
        """
        计算个人的计划工作量
        :param st_date: 起始日期
        :param ed_date: 截止日期
        :return:
        """

        _quota = 0.
        _ext_quota = 0.

        for _i in self.task:

            _issue_updated_date = _i["created"].split('T')[0]
            if handler.isDateBef(_issue_updated_date, st_date) or handler.isDateAft(_issue_updated_date, ed_date):
                continue

            if _i['org_time'] is None:
                continue

            if _i['ext']:
                _ext_quota += float(_i['org_time'])
            else:
                _quota += float(_i['org_time'])

        self.plan_quota = _quota
        self.ext_plan_quota = _ext_quota

    def get_plan_quota(self):
        """
        获取个人计划执工作量
        :return: 工作量
        """
        return self.plan_quota, self.ext_plan_quota

    def cal_quota(self, st_date, ed_date):
        """
        计算个人完成工作量
        :param st_date: 起始日期
        :param ed_date: 截止日期
        :return:
        """

        _quota = 0.
        _ext_quota = 0.

        for _i in self.task:

            _issue_updated_date = _i["updated"].split('T')[0]
            if handler.isDateBef(_issue_updated_date, st_date) or handler.isDateAft(_issue_updated_date, ed_date):
                continue

            """
            if u'完成' not in _i['status']:
                continue
            """
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
                if _i['ext']:
                    _ext_quota += _org_time
                else:
                    _quota += _org_time
            else:
                _miu = _org_time / _spent_time
                if _miu > 10:  # 预估时间严重失真
                    _miu = 1.3
                elif _miu > 5:  # 预估时间偏离过大
                    _miu = 1.2
                elif _miu > 1:  # 经验问题
                    _miu = 1.1
                if _i['ext']:
                    _ext_quota += (_spent_time * _miu)
                else:
                    _quota += (_spent_time * _miu)

        self.quota = _quota
        self.ext_quota = _ext_quota

    def get_quota(self):
        """
        获取个人任务完成工作量
        :return: 工作量（分本职的和支撑的，例如：针对产品研发人员，分"产品研发的"和"项目支撑的"）
        """
        return self.quota, self.ext_quota

    def cal_ind(self, st_date, ed_date):
        """
        计算个人工作指标
        :param st_date: 起始日期
        :param ed_date: 截止日期
        :return:
        """

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
