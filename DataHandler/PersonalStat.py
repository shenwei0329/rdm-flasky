#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
#
# 人员统计（基础）
# ============
# 用于管理所有人员信息
#
#
import mongodb_class
import sys
import member
import handler
import echart_handler

import logging

reload(sys)
sys.setdefaultencoding('utf-8')

"""特殊人员（不参与统计的）"""
spi_list = [u'王云枫', u'张嘉麒', u'何坤峰', u'唐高飞']
"""需要在"光荣榜"屏蔽的人员"""
spi_for_honor = [u'谭颖卿', u'向晓燕', u'吴丹阳', u'沈伟']
"""在组员分析时需要屏蔽的人员"""
spi_for_group = [u'谭颖卿', u'向晓燕', u'吴丹阳', u'沈伟', u'吴昱珉',
                 u'杨飞', u'柏银', u'王学凯', u'饶定远', u'王宇',
                 u'杨勇', u'李诗', u'金日海', u'雷东东', u'蒲治国'
                 u'何坤峰', u'刘伟'
                 ]
"""参与项目开发的部门"""
pj_devel_dpt = [u'行业营销部',
                u'解决方案与交付中心',
                u'新型智慧城市及运营商事业部']


class Personal:
    """
    构建个人信息库
    """

    def __init__(self, date=None, landmark=None):
        """
        构建
        :param date: 统计分析的起止日期
        :param landmark: （或）统计分析需指定的里程碑
        :return:
        """

        """人员集"""
        self.personal = {}

        """用于记录人员的归属部门"""
        self.members = {}

        self.mongodb = mongodb_class.mongoDB()
        self.landmark = landmark

        """用于做sankey图的参数"""
        self.nodes = []
        self.links = []
        self.plan_links = []

        """初始化统计日期"""
        if date is None:
            """本系统构建于2018年1月"""
            self.st_date = "2018-01-01"
            self.ed_date = "2018-12-31"
        else:
            self.st_date = date['st_date']
            self.ed_date = date['ed_date']
        """指定统计用的时标：created/updated"""
        self.whichdate = "created"

    def clearData(self):
        """
        清除信息【注：已废除】
        :return:
        """
        # self.personal = {}
        pass

    def setDate(self, date, whichdate=None):
        """
        为数据处理设置时间段
        :param date: 日期
        :param whichdate: 处理日期类型：created,updated
        :return:
        """
        self.st_date = date['st_date']
        self.ed_date = date['ed_date']
        if whichdate is not None:
            self.whichdate = whichdate

    def _getTaskListByPersonal(self, project, dpt, extTask):
        """
        按组列出 人员-任务
        :param project: 项目
        :param dpt: 部门
        :param extTask:
        :return:
        """

        """mongoDB数据库
        """
        self.mongodb.connect_db(project)

        if self.landmark is None:
            _search = {"issue_type": {"$ne": ["epic", "story"]},
                       "$or": [{"spent_time": {"$ne": None}},
                               {"org_time": {"$ne": None}}],
                       "$and": [{self.whichdate: {"$gte": "%s" % self.st_date}},
                                {self.whichdate: {"$lt": "%s" % self.ed_date}}]
                       }
        else:
            _search = {"issue_type": {"$ne": ["epic", "story"]},
                       "landmark": self.landmark,
                       "$or": [{"spent_time": {"$ne": None}},
                               {"org_time": {"$ne": None}}],
                       }
        _cur = self.mongodb.handler('issue', 'find', _search)

        if _cur.count() == 0:
            return

        for _issue in _cur:
            if _issue['users'] is None:
                continue
            if _issue['users'] in spi_list:
                continue
            if _issue['users'] not in self.members:
                # logging.log(logging.WARN, u">>> user(%s) not in members" % _issue['users'])
                continue

            if u"项目开发" in dpt:
                if self.members[_issue['users']] not in pj_devel_dpt:
                    continue
            else:
                if self.members[_issue['users']] not in dpt:
                    continue
            if _issue['users'] not in self.personal:
                self.personal[_issue['users']] = member.Member(_issue['users'], self.members[_issue['users']])
            _task = {}
            for _i in ['issue', 'summary', 'status', 'org_time',
                       'agg_time', 'spent_time', 'sprint', 'created', 'updated']:
                _task[_i] = _issue[_i]

            _issue_class = _issue['issue'].split('-')[0]
            if _issue_class in ['CPSJ', 'FAST', 'HUBBLE', 'ROOOT']:
                _task['ext'] = False
                if _issue in extTask:
                    _task['ext'] = True
            else:
                _task['ext'] = True

            self.personal[_issue['users']].add_task(_task)

    def _getWorklogListByPersonal(self, project):
        """
        按组列出 人员-工作日志
        :param project: 项目
        :return:
        """

        """mongoDB数据库
        """
        self.mongodb.connect_db(project)

        for _personal in self.personal:
            _search = {"author": u'%s' % _personal,
                       "$and": [{"updated": {"$gte": "%s" % self.st_date}},
                                {"updated": {"$lt": "%s" % self.ed_date}}]
                       }
            _cur = self.mongodb.handler('worklog', 'find', _search)

            if _cur.count() == 0:
                continue

            for _wl in _cur:
                _worklog = {}
                for _i in ['issue', 'comment', 'timeSpentSeconds', 'created', 'started', 'updated']:
                    _worklog[_i] = _wl[_i]
                self.personal[_personal].add_work_log(_worklog)

    def getWorklogSpentTime(self, name):
        """
        获取个人工作日志中工时统计
        :param name: 名称
        :return:
        """
        worklogs = self.personal[name].get_work_log()
        _spent_time = 0
        for _issue in worklogs:
            if _issue['timeSpentSeconds'] is None:
                continue
            _spent_time += float(_issue['timeSpentSeconds'])

        return _spent_time

    def getSumSpentTime(self, name):
        """
        获取个人任务中工时统计
        :param name: 名称
        :return:
        """
        issues = self.personal[name].get_task()
        _time = 0
        for _issue in issues:
            if _issue['spent_time'] is None:
                continue
            _time += float(_issue['spent_time'])

        return _time

    def getSpentTime(self, name):
        """
        获取个人任务中工时统计
        :param name: 名称
        :return:
        """
        issues = self.personal[name].get_task()
        _time = []
        for _issue in issues:
            if _issue['spent_time'] is None:
                continue
            _time.append(float(_issue['spent_time']))

        return _time

    def getDiffTime(self, name):
        """
        获取个人任务中执行时间与估计时间之差的统计
        :param name: 名称
        :return:
        """
        issues = self.personal[name].get_task()
        _time = 0
        for _issue in issues:
            if (_issue['org_time'] is None) or (_issue['spent_time'] is None):
                continue
            _time += (float(_issue['org_time']) - float(_issue['spent_time']))

        return _time

    def getSumOrgTime(self, name):
        """
        获取个人任务中工时统计
        :param name: 名称
        :return:
        """
        issues = self.personal[name].get_task()
        _time = 0
        for _issue in issues:
            if _issue['org_time'] is None:
                continue
            _time += float(_issue['org_time'])

        return _time

    def getOrgTime(self, name):
        """
        获取个人任务中工时统计
        :param name: 名称
        :return:
        """
        issues = self.personal[name].get_task()
        _time = []
        for _issue in issues:
            if _issue['org_time'] is None:
                continue
            _time.append(float(_issue['org_time']))

        return _time

    def getNumberDone(self, name):
        """
        获取个人已完成任务的统计
        :param name:
        :return:
        """
        issues = self.personal[name].get_task()
        _done = 0
        for _issue in issues:
            if _issue['status'] == u'完成':
                _done += 1
        return _done, float(_done*100)/float(len(issues))

    def scanMember(self):
        """
        获取公司全员信息
        :return:
        """
        self.mongodb.connect_db("ext_system")
        _cur = self.mongodb.handler("member", "find", {u'状态': "1"})
        self.members = {}
        for _m in _cur:
            # logging.log(logging.WARN, u'%s' % _m)
            self.members[_m[u'人员姓名']] = _m[u'部门']

    def scanProject(self, project, dpt, extTask):

        logging.log(logging.WARN, u">>> PersonalStat.scanProject(%s,%s)@(%s,%s)" %
                    (project, dpt, self.st_date, self.ed_date))

        self.scanMember()
        self._getTaskListByPersonal(project, dpt, extTask)
        self._getWorklogListByPersonal(project)
        self.calWorkInd()

    def getPersonal(self, name=None):
        """
        获取全员信息
        :param name: 或指定名称
        :return: 信息
        """
        if name is None:
            return self.personal
        else:
            return self.personal[name]

    def getNameList(self):
        """
        获取员工名称列表
        :return: 列表
        """
        return self.personal.keys()

    def getNumbOfTask(self, name):
        """
        获取指定员工的任务总数
        :param name: 员工名称
        :return: 任务总数
        """
        return len(self.personal[name].get_task())

    def getTotalNumbOfTask(self):
        """
        获取员工任务总数
        :return: 任务总数
        """
        _count = 0
        for _p in self.personal:
            _count += self.personal[_p].get_task_count()
        return _count

    def getTotalNumbOfWorkLog(self):
        """
        获取员工工作日志总数
        :return: 工作日志的总数
        """
        _count = 0
        for _p in self.personal:
            _count += self.personal[_p].get_work_log_count()
        return _count

    def getNumbOfMember(self):
        """
        获取员工个数
        :return: 个数
        """
        return len(self.personal)

    def calWorkInd(self):
        """
        计算个人工作量指标
        :return: 个人工作量指标集合
        """
        for _p in self.personal:
            self.personal[_p].cal_quota(self.st_date, self.ed_date)

    def calTaskInd(self):
        """
        计算个人任务量指标
        :return: 个人任务量指标集合
        """

        for _p in self.personal:
            self.personal[_p].cal_ind(self.st_date, self.ed_date)

    def getTaskIndList(self, ind_type):
        """
        获取指定指标类性（执行的，和完成的）个人任务指标
        :param ind_type: 指标类性，"doing"和"done"
        :return: 个人任务指标集
        """
        _ind = []
        _personal = []
        for _p in self.personal:

            if _p in spi_for_group:
                continue

            __ind = self.personal[_p].get_ind()
            if __ind is None:
                continue

            if ind_type == "doing":
                _ind.append(__ind["doing"])
            elif ind_type == "done":
                _ind.append(__ind["done"])
            elif ind_type == "spent_doing":
                _ind.append(__ind["spent_doing"])
            elif ind_type == "spent_done":
                _ind.append(__ind["spent_done"])
            else:
                continue
            _personal.append(_p)

        return _ind, _personal

    def getWorkIndList(self):
        """
        获取个人工作量指标列表（按量排序），注：不包含研发管理部组员。
        :return: 排序的人员-工作量序列
        """
        _personal = ()
        for _p in self.personal:
            if _p not in spi_for_honor:
                _q, _ext_q = self.personal[_p].get_quota()
                _personal += (_p, int(_q + _ext_q),),

        return sorted(_personal, key=lambda x: x[1], reverse=True)

    def _add_link(self, source, target, value):
        """
        添加"工作量"链接
        :param source: 源
        :param target: 目标
        :param value: 值
        :return:
        """
        _link = {'source': source, 'target': target, 'value': value}
        if _link not in self.links:
            self.links.append(_link)

    def _add_plan_link(self, source, target, value):
        """
        添加"计划"链接
        :param source: 源
        :param target: 目标
        :param value: 值
        :return:
        """
        _link = {'source': source, 'target': target, 'value': value}
        if _link not in self.links:
            self.plan_links.append(_link)

    def buildSanKey(self, date):
        """
        按指定日期（通常为一个月）构建"个人-任务量-产品研发与项目支撑"的sankey图
        :param date: 一组日期（通常按一个月为一个单元），如[{'year': 2018, 'month': 3},...]
        :return: echarts图
        """

        self.nodes = []
        self.links = []

        for _date in date:

            """获取指定日期
            """
            year = _date['year']
            month = _date['month']

            """计算指定日期的起始、截止日期
            """
            _v = handler.cal_one_month(year, month)
            _st_date = _v['st_date']
            _ed_date = _v['ed_date']

            """节点："系统研发"、"项目支撑"和"日期"（含"【支撑】"的日期）
            """
            _str = "%d-%02d" % (year, month)

            logging.log(logging.WARN, ">>> PersonalStat.buildSanKey: %s,%s,%s" % (_st_date, _ed_date, _str))

            if {'name': u'产品研发'} not in self.nodes:
                self.nodes.append({'name': u'产品研发'})
            if {'name': u'项目支撑'} not in self.nodes:
                self.nodes.append({'name': u'项目支撑'})

            if {'name': _str} not in self.nodes:
                self.nodes.append({'name': _str})
            if {'name': _str+u'【支撑】'} not in self.nodes:
                self.nodes.append({'name': _str+u'【支撑】'})

            _month_quota = 0.
            _ext_month_quota = 0.
            _plan_month_quota = 0.
            _plan_ext_month_quota = 0.

            for _p in self.personal:
                """创建个人节点及其工作量链接
                """
                _node = {'name': _p}
                if _node not in self.nodes:
                    self.nodes.append(_node)
                self.personal[_p].cal_plan_quota(_st_date, _ed_date)
                self.personal[_p].cal_quota(_st_date, _ed_date)

                _q, _ext_q = self.personal[_p].get_quota()
                _month_quota += _q
                _ext_month_quota += _ext_q
                """建立"个人"与"日期"之间基于工作量的链接
                """
                self._add_link(_p, "%d-%02d" % (year, month), _q)
                self._add_link(_p, u"%d-%02d【支撑】" % (year, month), _ext_q)

                _q, _ext_q = self.personal[_p].get_plan_quota()
                """建立"个人"与"日期"之间基于计划工作量的链接
                """
                _plan_month_quota += _q
                _plan_ext_month_quota += _ext_q
                self._add_plan_link(_p, "%d-%02d" % (year, month), _q)
                self._add_plan_link(_p, u"%d-%02d【支撑】" % (year, month), _ext_q)

            """建立"日期"与"产品研发"之间基于工作量的链接
            """
            self._add_link("%d-%02d" % (year, month), u'产品研发', _month_quota)
            self._add_link(u"%d-%02d【支撑】" % (year, month), u'项目支撑', _ext_month_quota)

            """建立"日期"与"产品研发"之间基于计划工作量的链接
            """
            self._add_plan_link("%d-%02d" % (year, month), u'产品研发', _plan_month_quota)
            self._add_plan_link(u"%d-%02d【支撑】" % (year, month), u'项目支撑', _plan_ext_month_quota)

        return echart_handler.sankey_charts('', self.nodes, self.links)

