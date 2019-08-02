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
#   通过个人档案建立以人为主题的（至少是本年度的全量）数据集，实现“事”的聚集，并通过人与事之间的不同维度的数据分析建立个人最核心的价值描述。
#   目前的数据：
#       -）基本信息：姓名、邮箱、职级、岗位、归属部门
#       -）任务与执行：当前任务分配的饱满程度、执行情况、偏向产品研发或项目开发
#       -）工作日志：可衡量出1个spent_time对应了多少个work_hour，简介说明任务的"难度"
#       -）考勤：出勤情况，应该是全勤，可细节上看看一些作息的习惯，早上上班时间分布，晚上下班时间分布，按天、周、月等
#       -）差旅：差旅情况，是否经常出差？
#
#   个人有哪些特征？
#       -）任务分布情况
#       -）任务执行特点：哪类任务？执行任务是否具有明显特征（按时间等）？任务与工作日志的关联特征？与团队的关系？对外支撑特征？
#       -）是否经常早到？是否经常晚走？加班是否及时换休？
#       -）是否经常出差？
#
#   如何有效评价？
#       评价模型理论上应该建立在个人特征的综合评判的结果基础上，每个特征可按不同的权重计算。
#

import mongodb_class
import handler
import sys
import logging

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
        self.m = []
        # logging.log(logging.WARN, u">>> Member.__init__(%s,%s,%s)" % (self.name, self.dpt, self.email))

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

    def get_dpt(self):
        return self.dpt

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
            if handler.is_date_bef(_issue_updated_date, st_date) or handler.is_date_aft(_issue_updated_date, ed_date):
                continue

            if _i['org_time'] is None:
                continue

            if _i['ext']:
                _ext_quota += float(_i['org_time'])
            else:
                _quota += float(_i['org_time'])

        self.plan_quota = _quota
        self.ext_plan_quota = _ext_quota

    def cal_plan_quota_for_pj(self, st_date, ed_date):
        """
        计算个人的计划工作量
        :param st_date: 起始日期
        :param ed_date: 截止日期
        :return:
        """

        _ret = {}
        _quota = 0.

        for _i in self.task:

            _pj_name = _i['issue'].split('-')[0]
            if _pj_name not in _ret:
                _ret[_pj_name] = 0.

            _issue_updated_date = _i["created"].split('T')[0]
            if handler.is_date_bef(_issue_updated_date, st_date) or handler.is_date_aft(_issue_updated_date, ed_date):
                continue

            if _i['org_time'] is None:
                continue

            _quota += float(_i['org_time'])

        _ret[_pj_name] = _quota
        self.plan_quota = _ret
        self.ext_plan_quota = _ret

    def get_plan_quota(self):
        """
        获取个人计划执工作量
        :return: 工作量
        """
        return self.plan_quota, self.ext_plan_quota

    def cal_quota(self, st_date, ed_date, log_enabled=False):
        """
        计算个人完成工作量
        :param st_date: 起始日期
        :param ed_date: 截止日期
        :param log_enabled: 是否记录日志
        :return:
        """

        _quota = 0.
        _ext_quota = 0.
        _m = []

        for _i in self.task:

            _issue_updated_date = _i["updated"].split('T')[0]
            if handler.is_date_bef(_issue_updated_date, st_date) or handler.is_date_aft(_issue_updated_date, ed_date):
                # print("%s:%s:%s" % (st_date, _issue_updated_date, ed_date))
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
                if u'完成' in _i['status']:
                    _m.append(1.0)
            else:
                _miu = _org_time / _spent_time
                if u'完成' in _i['status']:
                    if _miu > 2:
                        _miu = 2.2
                    _m.append(_miu)
                if _miu > float(handler.conf.get('QUOTA', 'high_ratio_level')):
                    # 预估时间严重失真
                    _miu = float(handler.conf.get('QUOTA', 'high_ratio_value'))
                elif _miu > float(handler.conf.get('QUOTA', 'middle_ratio_level')):
                    # 预估时间偏离过大
                    _miu = float(handler.conf.get('QUOTA', 'middle_ratio_value'))
                elif _miu > handler.conf.get('QUOTA', 'low_ratio_level'):
                    # 经验问题
                    _miu = float(handler.conf.get('QUOTA', 'low_ratio_value'))

                if _i['ext']:
                    _ext_quota += (_spent_time * _miu)
                else:
                    _quota += (_spent_time * _miu)

        if log_enabled:
            logging.log(logging.WARN, u">>>个人任务完成记录：<%s>-<%s> [%s]:%s" % (st_date, ed_date, self.name, _m))

        self.m = _m
        self.quota = _quota
        self.ext_quota = _ext_quota

    def cal_quota_for_pj(self, st_date, ed_date, log_enabled=False):
        """
        计算个人完成工作量（面向项目资源）
        :param st_date: 起始日期
        :param ed_date: 截止日期
        :param log_enabled: 是否记录日志
        :return:
        """

        _ret = {}
        _quota = 0.
        _m = []

        for _i in self.task:

            _pj_name = _i['issue'].split('-')[0]
            if _pj_name not in _ret:
                _ret[_pj_name] = 0.

            _issue_updated_date = _i["updated"].split('T')[0]
            if handler.is_date_bef(_issue_updated_date, st_date) or handler.is_date_aft(_issue_updated_date, ed_date):
                # print("%s:%s:%s" % (st_date, _issue_updated_date, ed_date))
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
                _quota += _org_time
                if u'完成' in _i['status']:
                    _m.append(1.)
            else:
                _miu = _org_time / _spent_time
                if u'完成' in _i['status']:
                    if _miu > 2:
                        _miu = 2.2
                    _m.append(_miu)
                if _miu > float(handler.conf.get('QUOTA', 'high_ratio_level')):
                    # 预估时间严重失真
                    _miu = float(handler.conf.get('QUOTA', 'high_ratio_value'))
                elif _miu > float(handler.conf.get('QUOTA', 'middle_ratio_level')):
                    # 预估时间偏离过大
                    _miu = float(handler.conf.get('QUOTA', 'middle_ratio_value'))
                elif _miu > handler.conf.get('QUOTA', 'low_ratio_level'):
                    # 经验问题
                    _miu = float(handler.conf.get('QUOTA', 'low_ratio_value'))

                _quota += (_spent_time * _miu)

            _ret[_pj_name] = _quota

        if log_enabled:
            logging.log(logging.WARN, u">>>个人任务完成记录：<%s>-<%s> [%s]:%s" % (st_date, ed_date, self.name, _m))

        self.m = _m
        self.quota = _ret
        self.ext_quota = _ret

    def get_quota(self):
        """
        获取个人任务完成工作量
        :return: 工作量（分本职的和支撑的，例如：针对产品研发人员，分"产品研发的"和"项目支撑的"）
        """
        return self.quota, self.ext_quota

    def get_m(self):
        return self.m

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
        _agg_doing = 0
        _agg_done = 0
        _ind = {}
        for _i in self.task:

            _issue_updated_date = _i["updated"].split('T')[0]
            if handler.is_date_bef(_issue_updated_date, st_date) or handler.is_date_aft(_issue_updated_date, ed_date):
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

            if _i['agg_time'] is not None:
                if u'完成' not in _i['status']:
                    _agg_doing += _i['agg_time']
                else:
                    _agg_done += _i['agg_time']

        _ind['doing'] = _doing / 3600
        _ind['done'] = _done / 3600
        _ind['spent_doing'] = _spent_doing / 3600
        _ind['spent_done'] = _spent_done / 3600
        _ind['agg_doing'] = _agg_doing / 3600
        _ind['agg_done'] = _agg_done / 3600

        self.ind = _ind

    def get_ind(self):
        """
        获取个人工作指标
        :return: 指标
        """
        return self.ind

    def add_checkon(self, check_on_work):
        """
        添加出勤信息
        :param check_on_work: 上下班及请假记录
        :return:
        """
        pass

    def cal_checkon(self):
        """
        计算出勤指标
        :return: 指标
        """
        pass

    def add_travel(self, travel):
        """
        添加出差信息
        :param travel: 出差请求
        :return:
        """
        pass

    def cal_travel(self):
        """
        计算出差指标
        :return: 指标
        """
        pass

    def cal_kpi_ind(self):
        """
        计算个人综合指标
        :return: 指标
        """
        pass

