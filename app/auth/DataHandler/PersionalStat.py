#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
#
#
#

import mongodb_class


class Persional:
    """
    构建个人信息库
    """

    def __init__(self, st_date, ed_date):
        self.Persional = {}
        self.mongodb = mongodb_class.mongoDB(None)
        self.st_date = st_date
        self.ed_date = ed_date

    def _getTaskListByPersion(self, project):
        """
        按组列出 人员-任务
        :param project: 项目
        :return:
        """

        """mongoDB数据库
        """
        self.mongodb.setDataBbase(project)

        _search = {"issue_type": u"任务",
                   "$and": [{"created": {"$gte": "%s" % self.st_date}},
                            {"created": {"$lt": "%s" % self.ed_date}}]
                   }
        _cur = self.mongodb.handler('issue', 'find', _search)

        if _cur.count() == 0:
            return

        for _issue in _cur:
            if _issue['users'] is None:
                continue
            if _issue['users'] not in self.Persional:
                self.Persional[_issue['users']] = {'issue': [], 'worklog': []}
            _task = {}
            for _i in ['issue', 'summary', 'status', 'org_time',
                       'agg_time', 'spent_time', 'sprint', 'created', 'updated']:
                _task[_i] = _issue[_i]
            self.Persional[_issue['users']]['issue'].append(_task)

    def _getWorklogListByPersion(self, project):
        """
        按组列出 人员-工作日志
        :param project: 项目
        :return:
        """

        """mongoDB数据库
        """
        self.mongodb.setDataBbase(project)

        for _persion in self.Persional:
            _search = {"author": u'%s' % _persion,
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
                self.Persional[_persion]['worklog'].append(_worklog)

    def getWorklogSpentTime(self, name):
        """
        获取个人工作日志中工时统计
        :param name: 名称
        :return:
        """
        worklogs = self.Persional[name]['worklog']
        _spent_time = 0
        for _issue in worklogs:
            if _issue['timeSpentSeconds'] is None:
                continue
            _spent_time += float(_issue['timeSpentSeconds'])

        return _spent_time

    def getSpentTime(self, name):
        """
        获取个人任务中工时统计
        :param name: 名称
        :return:
        """
        issues = self.Persional[name]['issue']
        _spent_time = 0
        for _issue in issues:
            if _issue['spent_time'] is None:
                continue
            _spent_time += float(_issue['spent_time'])

        return _spent_time

    def getNumberDone(self, name):
        """
        获取个人已完成任务的统计
        :param name:
        :return:
        """
        issues = self.Persional[name]['issue']
        _done = 0
        for _issue in issues:
            if _issue['status'] == u'完成':
                _done += 1
        return _done, float(_done*100)/float(len(issues))

    def dispPersion(self, persion):
        """
        显示个人业绩
        :param persion: 个人数据汇总
        :return:
        """
        for _name in persion:
            _done, _ratio = self.getNumberDone(persion[_name]['issue'])
            print(u'>>> %s: Task=%d, Done=%d, R=%0.2f%%, Spent=%0.2f (工时)' % (
                _name,
                len(persion[_name]['issue']),
                _done,
                _ratio,
                self.getSpentTime(_name)/3600.))

    def clearPersional(self):
        self.Persional = {}

    def scanProject(self, project):
        self._getTaskListByPersion(project)
        self._getWorklogListByPersion(project)

    def getPersional(self, name=None):
        if name is None:
            return self.Persional
        else:
            return self.Persional[name]

    def getNameList(self):
        return self.Persional.keys()

    def getNumbOfTask(self, name):
        return len(self.Persional[name]['issue'])

    def getNumbOfMember(self):
        return len(self.Persional)
