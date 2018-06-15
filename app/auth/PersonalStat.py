#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
#
#
#
import mongodb_class
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

spi_list = [u'王云枫', u'张嘉麒', u'何坤峰', u'唐高飞']
spi_for_honor = [u'谭颖卿', u'向晓燕', u'吴丹阳', u'沈伟']
spi_for_group = [u'谭颖卿', u'向晓燕', u'吴丹阳', u'沈伟', u'吴昱珉',
                 u'杨飞', u'柏银', u'王学凯', u'饶定远', u'王宇',
                 u'杨勇', u'李诗', u'金日海', u'雷东东', u'蒲治国'
                 u'何坤峰', u'刘伟'
                 ]


class Personal:
    """
    构建个人信息库
    """

    def __init__(self, date=None, landmark=None):
        self.personal = {}
        self.mongodb = mongodb_class.mongoDB()
        self.landmark = landmark
        if date is None:
            self.st_date = "2018-01-01"
            self.ed_date = "2018-12-31"
        else:
            self.st_date = date['st_date']
            self.ed_date = date['ed_date']
        self.whichdate = "created"

    def clearData(self):
        self.personal = {}

    def setDate(self, date, whichdate=None):
        self.st_date = date['st_date']
        self.ed_date = date['ed_date']
        if whichdate is not None:
            self.whichdate = whichdate


    def _getTaskListByPersonal(self, project):
        """
        按组列出 人员-任务
        :param project: 项目
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
            if _issue['users'] not in self.personal:
                self.personal[_issue['users']] = {'issue': [], 'worklog': [], 'quota': 0.}
            _task = {}
            for _i in ['issue', 'summary', 'status', 'org_time',
                       'agg_time', 'spent_time', 'sprint', 'created', 'updated']:
                _task[_i] = _issue[_i]
            self.personal[_issue['users']]['issue'].append(_task)

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
                       "$and": [{"started": {"$gte": "%s" % self.st_date}},
                                {"started": {"$lt": "%s" % self.ed_date}}]
                       }
            _cur = self.mongodb.handler('worklog', 'find', _search)

            if _cur.count() == 0:
                continue

            _worklog = {}
            for _wl in _cur:
                for _i in ['issue', 'comment', 'timeSpentSeconds', 'created', 'started', 'updated']:
                    _worklog[_i] = _wl[_i]
                self.personal[_personal]['worklog'].append(_worklog)

    def getWorklogSpentTime(self, name):
        """
        获取个人工作日志中工时统计
        :param name: 名称
        :return:
        """
        worklogs = self.personal[name]['worklog']
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
        issues = self.personal[name]['issue']
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
        issues = self.personal[name]['issue']
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
        issues = self.personal[name]['issue']
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
        issues = self.personal[name]['issue']
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
        issues = self.personal[name]['issue']
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
        issues = self.personal[name]['issue']
        _done = 0
        for _issue in issues:
            if _issue['status'] == u'完成':
                _done += 1
        return _done, float(_done*100)/float(len(issues))

    def dispPersonal(self, personal):
        """
        显示个人业绩
        :param persion: 个人数据汇总
        :return:
        """
        for _name in personal:
            _done, _ratio = self.getNumberDone(personal[_name]['issue'])
            print(u'>>> %s: Task=%d, Done=%d, R=%0.2f%%, Spent=%0.2f (工时)' % (
                  _name,
                  len(personal[_name]['issue']),
                  _done,
                  _ratio,
                  self.getSpentTime(_name)/3600.)
                  )

    def clearPersonal(self):
        self.personal = {}

    def scanProject(self, project):
        self._getTaskListByPersonal(project)
        self._getWorklogListByPersonal(project)
        self.calWorkInd()

    def getPersonal(self, name=None):
        if name is None:
            return self.personal
        else:
            return self.personal[name]

    def getNameList(self):
        return self.personal.keys()

    def getNumbOfTask(self, name):
        return len(self.personal[name]['issue'])

    def getTotalNumbOfTask(self):
        _count = 0
        for _p in self.personal:
            _count += len(self.personal[_p]['issue'])
        return _count

    def getTotalNumbOfWorkLog(self):
        _count = 0
        for _p in self.personal:
            _count += len(self.personal[_p]['worklog'])
        return _count

    def getNumbOfMember(self):
        return len(self.personal)

    def calWorkInd(self):
        """
        计算个人工作量指标
        :return: 个人工作量指标集合
        """

        for _p in self.personal:
            _quota = 0.
            for _i in self.personal[_p]['issue']:
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
                    _miu = _org_time/_spent_time
                    if _miu > 10:   # 预估时间严重失真
                        _miu = 1.8
                    elif _miu > 5:  # 预估时间偏离过大
                        _miu = 1.5
                    elif _miu > 1:  # 经验问题
                        _miu = 1.3
                    _quota += (_org_time*_miu)
            self.personal[_p]['quota'] = _quota

    def calTaskInd(self):
        """
        计算个人任务量指标
        :return: 个人任务量指标集合
        """

        for _p in self.personal:
            _doing = 0
            _done = 0
            _spent_doing = 0
            _spent_done = 0
            for _i in self.personal[_p]['issue']:
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

            self.personal[_p]['doing'] = _doing/3600
            self.personal[_p]['done'] = _done/3600
            self.personal[_p]['spent_doing'] = _spent_doing/3600
            self.personal[_p]['spent_done'] = _spent_done/3600

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

            if ind_type == "doing":
                _ind.append(self.personal[_p]["doing"])
            elif ind_type == "done":
                _ind.append(self.personal[_p]["done"])
            elif ind_type == "spent_doing":
                _ind.append(self.personal[_p]["spent_doing"])
            elif ind_type == "spent_done":
                _ind.append(self.personal[_p]["spent_done"])
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
                _personal += (_p, int(self.personal[_p]['quota']),),

        return sorted(_personal, key=lambda x: x[1], reverse=True)

