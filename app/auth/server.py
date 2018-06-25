#coding=utf-8

from __future__ import unicode_literals

import echart_handler
import handler
import pandas as pd
import datetime
import numpy as np
from flask_login import current_user
from ..models import Role
import PersonalStat
import logging

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

# 产品研发中心
pd_databases = ['CPSJ',
                'FAST',
                'HUBBLE',
                'ROOOOT']

# 项目开发组
pj_databases = ['JX',
                'GZ',
                'SCGA',
                'FT']

# 研发管理与测试部
rdm_databases = ['RDM',
                 'TESTCENTER']

# 月份
month = [u'一月', u'二月', u'三月', u'四月', u'五月', u'六月', u'七月', u'八月', u'九月', u'十月', u'十一月', u'十二月']

# 人员职级
level = [u'职级1',
         u'职级2',
         u'职级3',
         u'职级4',
         u'职级5',
         u'职级6',
         u'职级7',
         u'职级8',
         u'职级9',
         u'职级10',
         u'职级11',
         u'职级12',
         ]

# 全局日期
st_date = '2018-01-01'
ed_date = '2018-12-31'

"""产品研发中心人员"""
pdPersonals = PersonalStat.Personal()
"""项目开发人员"""
pjPersonals = PersonalStat.Personal()
"""研发管理与测试人员"""
rdmPersonals = PersonalStat.Personal()
"""产品研发中心对外支撑任务"""
extTask = None


def calTaskInd(_type):
    global pdPersonals, pjPersonals, rdmPersonals

    _sum = 0
    _task = {}
    _personal = {}
    pdPersonals.calTaskInd()
    _task['pd'], _personal['pd'] = pdPersonals.getTaskIndList(_type)
    pjPersonals.calTaskInd()
    _task['pj'], _personal['pj'] = pjPersonals.getTaskIndList(_type)
    rdmPersonals.calTaskInd()
    _task['rdm'], _personal['rdm'] = rdmPersonals.getTaskIndList(_type)

    dots = {}
    for _g in ['pd', 'pj', 'rdm']:
        """中值"""
        # _task_median = np.median(_task[_g])
        # _task_std = np.std(_task[_g])
        _sum += sum(_task[_g])

        # print(">>> %d, %d" % (_task_median, _task_std))

        _dot = {'low': {'x': [], 'y': []},
                'norm': {'x': [], 'y': []},
                'high': {'x': [], 'y': []},
                }
        _cnt = 0
        for _yy in range(1, 11):
            if _cnt >= len(_task[_g]):
                break
            for _xx in range(1, 21):
                if _cnt >= len(_task[_g]):
                    break
                # if _task[_g][_cnt] > _task_median + _task_std:
                if _task[_g][_cnt] > 40:
                    _dot['high']['x'].append(_xx)
                    _dot['high']['y'].append(_yy)
                # elif _task[_g][_cnt] >= _task_median:
                elif _task[_g][_cnt] >= 24:
                    _dot['norm']['x'].append(_xx)
                    _dot['norm']['y'].append(_yy)
                else:
                    _dot['low']['x'].append(_xx)
                    _dot['low']['y'].append(_yy)
                    # print(u">>> G(%s)-LOW.<%s>" % (_g, _personal[_g][_cnt]))
                _cnt += 1

        dots[_g] = _dot

    return dots, _sum


def calTaskIndByDate(_type, _st_date, _ed_date):
    """
    按指定时间段统计每个组（产品研发、项目开发、研发管理与测试）的任务量
    :param _type: 日期项，created/updated
    :param _st_date: 起始日期
    :param _ed_date: 截止日期
    :return: 统计结果
    """
    global pdPersonals, pjPersonals, rdmPersonals

    """设置统计日期，并完成相关统计"""
    setPersonalDate(_st_date, _ed_date)

    _sum = 0
    _personal = {}
    _task = {}

    """计算组员的任务指标"""
    _t, _p = pdPersonals.getTaskIndList(_type)
    _personal['pd'] = _p
    _task['pd'] = _t
    _t, _p = pjPersonals.getTaskIndList(_type)
    _personal['pj'] = _p
    _task['pj'] = _t
    _t, _p = rdmPersonals.getTaskIndList(_type)
    _personal['rdm'] = _p
    _task['rdm'] = _t

    dots = {}
    for _g in ['pd', 'pj', 'rdm']:
        """中值"""
        # _task_median = np.median(_task[_g])
        # _task_std = np.std(_task[_g])
        # print(">>> %d, %d" % (_task_median, _task_std))

        """每个组的矩阵按 20（列）xN（行）排列，N=[1,10]
        """
        _dot = {'low': {'x': [], 'y': [], 'label': []},
                'norm': {'x': [], 'y': [], 'label': []},
                'high': {'x': [], 'y': [], 'label': []},
                }
        _cnt = 0
        for _yy in range(1, 11):
            """取值1～10"""
            if _cnt >= len(_task[_g]):
                break
            for _xx in range(1, 21):
                """取值1～20"""
                if _cnt >= len(_task[_g]):
                    break

                # if _task[_g][_cnt] > _task_median + _task_std:
                if _task[_g][_cnt] > 40:
                    """超负荷：具有5天8小时工作量"""
                    _dot['high']['x'].append(_xx)
                    _dot['high']['y'].append(_yy)
                    _dot['high']['label'].append(_personal[_g][_cnt])
                # elif _task[_g][_cnt] >= _task_median:
                elif _task[_g][_cnt] >= 24:
                    """适度：具有3天8小时工作量"""
                    _dot['norm']['x'].append(_xx)
                    _dot['norm']['y'].append(_yy)
                    _dot['norm']['label'].append(_personal[_g][_cnt])
                else:
                    """欠计划"""
                    _dot['low']['x'].append(_xx)
                    _dot['low']['y'].append(_yy)
                    _dot['low']['label'].append(_personal[_g][_cnt])
                    # print(u">>> G(%s)-LOW.<%s>" % (_g, _personal[_g][_cnt]))
                _cnt += 1

        dots[_g] = _dot

    return dots, sum(_task['pd'])



def set_manager_context():

    _x, _y = handler.nTaskByLevel(pdPersonals)
    _xs, _ys = handler.spentTimeSumByLevel(pdPersonals)
    _xo, _yo = handler.orgTimeSumByLevel(pdPersonals)
    _xd, _yd = handler.diffTimeByLevel(pdPersonals)

    _context = dict()
    role = Role.query.filter_by(name=current_user.username).first()
    print(">>> role.level = %d" % role.level)
    _context['user'] = {'role': role.level}
    _context['pic'] = echart_handler.effectscatter('职级-任务量',
                                                   [{"x": _x, "y": _y}],
                                                   size={'width': 640, 'height': 420})
    _context['pic_time'] = echart_handler.effectscatter('职级-时间',
                                                        [{"x": _xo, "y": _yo}, {"x": _xs, "y": _ys}],
                                                        size={'width': 640, 'height': 420})
    _context['pic_diff'] = echart_handler.effectscatter('职级-时间差',
                                                        [{"x": _xd, "y": _yd}],
                                                        size={'width': 640, 'height': 420})
    _context['pic_sankey'] = pdPersonals.buildSanKey([{'year': 2018, 'month': 4},
                                                      {'year': 2018, 'month': 5},
                                                      {'year': 2018, 'month': 6},
                                                      ])

    return _context


def setPersonalDate(_st_date, _ed_date):
    """
    设置人员的统计起止日期，并完成任务、工作指标计算
    :param _st_date: 开始日期
    :param _ed_date: 截止日期
    :return:
    """

    global pdPersonals, pjPersonals, rdmPersonals

    pdPersonals.setDate(date={'st_date': _st_date, 'ed_date': _ed_date}, whichdate="updated")
    pjPersonals.setDate(date={'st_date': _st_date, 'ed_date': _ed_date}, whichdate="updated")
    rdmPersonals.setDate(date={'st_date': _st_date, 'ed_date': _ed_date}, whichdate="updated")

    """计算人员的任务量
    """
    pdPersonals.calTaskInd()
    pjPersonals.calTaskInd()
    rdmPersonals.calTaskInd()

    """计算人员的工作量
    """
    pdPersonals.calWorkInd()
    pjPersonals.calWorkInd()
    rdmPersonals.calWorkInd()


def set_honor_context(_st_date, _ed_date):
    """
    设置“光荣榜”的context内容
    :param st_date: 工作量计量的起始日期
    :param ed_date: 工作量计量的终止日期
    :return: context
    """
    global ed_date, st_date, pdPersonals, pjPersonals, rdmPersonals

    if _ed_date is None:
        _ed_date = ed_date
    if _st_date is None:
        _st_date = st_date

    # logging.log(logging.WARN, ">>> server.set_honour_context(%s,%s)" % (_st_date, _ed_date))

    setPersonalDate(_st_date, _ed_date)

    _pd_work_ind = pdPersonals.getWorkIndList()
    _pj_work_ind = pjPersonals.getWorkIndList()
    _rdm_work_ind = rdmPersonals.getWorkIndList()

    """设置上榜人员个数,按每行6人显示
    """
    _pd_count = handler.conf.getint('HONOR', 'pd_number_member')
    _pd_numb_list = _pd_count/handler.conf.getint('HONOR', 'number_column')

    _pj_count = handler.conf.getint('HONOR', 'pj_number_member')
    _pj_numb_list = _pj_count/handler.conf.getint('HONOR', 'number_column')

    _rdm_count = handler.conf.getint('HONOR', 'rdm_number_member')
    _rdm_numb_list = _rdm_count/handler.conf.getint('HONOR', 'number_column')

    _pd_list = []
    _pj_list = []
    _rdm_list = []

    for _i in range(_pd_numb_list):
        _personal = []
        for _j in range(handler.conf.getint('HONOR', 'number_column')):
            _item = _pd_work_ind[_i*handler.conf.getint('HONOR', 'number_column') + _j]
            # logging.log(logging.WARN, ">>> %s:%d" % (_item[0], _item[1]))
            _personal.append({'name': _item[0], 'quota': _item[1]})
        _pd_list.append(_personal)

    for _i in range(_pj_numb_list):
        _personal = []
        for _j in range(handler.conf.getint('HONOR', 'number_column')):
            _item = _pj_work_ind[_i*handler.conf.getint('HONOR', 'number_column') + _j]
            # logging.log(logging.WARN, ">>> %s:%d" % (_item[0], _item[1]))
            _personal.append({'name': _item[0], 'quota': _item[1]})
        _pj_list.append(_personal)

    for _i in range(_rdm_numb_list):
        _personal = []
        for _j in range(handler.conf.getint('HONOR', 'number_column')):
            _item = _rdm_work_ind[_i*handler.conf.getint('HONOR', 'number_column') + _j]
            # logging.log(logging.WARN, ">>> %s:%d" % (_item[0], _item[1]))
            _personal.append({'name': _item[0], 'quota': _item[1]})
        _rdm_list.append(_personal)

    _context = dict(
        pd_list=_pd_list,
        pj_list=_pj_list,
        rdm_list=_rdm_list,
        pd_numb=range(_pd_numb_list),
        pj_numb=range(_pj_numb_list),
        rdm_numb=range(_rdm_numb_list),
    )
    return _context

def set_pd_context():

    _pd = handler.get_product_shelves()
    _dl = handler.get_product_deliver()
    context = dict(
        products=_pd,
        pd_total=len(_pd),
        pd_delivers=_dl,
        dl_total=len(_dl)
    )
    
    return context


def scan_project_name(project_info, summary):
    """
    从summary中寻找项目信息
    :param project_info: 项目信息
    :param summary: summary
    :return: 项目名称
    """

    for _pj in project_info:
        if _pj[u'别名'] in summary:
            return _pj[u'名称']
    # print(u">>> summary: %s" % summary)
    return None


def calPjTaskInd(_st_date, _ed_date):
    """
    计算产品研发中心资源投入到非产品事务的指标。
    :param _st_date: 起始日期
    :param _ed_date: 截止日期
    :return: 统计指标
    """
    global extTask

    _pj_info = handler.get_project_info("project_t")

    # logging.log(logging.WARN, ">>> calPjTaskInd( %s, %s )" % (_st_date, _ed_date))

    _pj_sum = 0
    _npj_sum = 0
    _project = {}
    for _issue in extTask:

        if _issue["updated"] is None:
            continue

        _issue_updated_date = _issue["updated"].split('T')[0]
        """判断任务是否在指定的时间段内"""
        if handler.isDateBef(_issue_updated_date, _st_date) or handler.isDateAft(_issue_updated_date, _ed_date):
            continue

        _group = _issue['issue'].split('-')[0]

        if _issue['project_alias'] is not None:
            if _issue['project_alias'] not in _project:
                _project[_issue['project_alias']] = {_group: _issue['spent_time']}
            else:
                if _group not in _project[_issue['project_alias']]:
                    _project[_issue['project_alias']][_group] = _issue['spent_time']
                else:
                    _project[_issue['project_alias']][_group] += _issue['spent_time']
            _pj_sum += _issue['spent_time']
        else:
            """试图从summary中寻找项目信息"""
            _pj_name = scan_project_name(_pj_info, _issue['summary'])
            if _pj_name is not None:
                """有项目信息"""
                if _pj_name not in _project:
                    _project[_pj_name] = {_group: _issue['spent_time']}
                else:
                    if _group not in _project[_pj_name]:
                        _project[_pj_name][_group] = _issue['spent_time']
                    else:
                        _project[_pj_name][_group] += _issue['spent_time']
                _pj_sum += _issue['spent_time']
            else:
                """无项目信息"""
                if u'其它' not in _project:
                    _project[u'其它'] = {_group: _issue['spent_time']}
                else:
                    if _group not in _project[u'其它']:
                        _project[u'其它'][_group] = _issue['spent_time']
                    else:
                        _project[u'其它'][_group] += _issue['spent_time']
                _npj_sum += _issue['spent_time']

    # logging.log(logging.WARN, ">>> return %s, %d, %d" % (_project, _pj_sum, _npj_sum))
    return _project, _pj_sum, _npj_sum


def projectSum(_project):

    for _pj in _project:
        _sum = 0
        for _g in _project[_pj]:
            _sum += _project[_pj][_g]
        _project[_pj][u'合计'] = _sum


def set_rdm_context():

    global pdPersonals, pjPersonals, rdmPersonals, extTask, st_date, ed_date

    """项目归档情况
    """
    pj = []
    _m = handler.get_material()
    _count = _m.count()
    for __m in _m:
        if __m[u'项目名称'] not in pj:
            pj.append(__m[u'项目名称'])

    _ext_personals_stat = handler.get_project_info('ext_personals_stat')

    role = Role.query.filter_by(name=current_user.username).first()

    if role.level <= 2 or role.level == 66:
        """产品研发投入项目开发情况
        """
        _project, _pj_sum, _npj_sum = calPjTaskInd(st_date, ed_date)
        """近三个月的日期"""
        __v = handler.calDateMonthly(3)
        _st_date_3m = __v['st_date']
        _ed_date_3m = __v['ed_date']
        _project_3m, _pj_sum_3m, _npj_sum_3m = calPjTaskInd(_st_date_3m, _ed_date_3m)

        """上一个月的日期"""
        __v = handler.calDateMonthly(1)
        _st_date_1m = __v['st_date']
        _ed_date_1m = __v['ed_date']
        _project_1m, _pj_sum_1m, _npj_sum_1m = calPjTaskInd(_st_date_1m, _ed_date_1m)

        projectSum(_project)
        projectSum(_project_1m)
        projectSum(_project_3m)

        _npj_sum = _npj_sum/3600
        _pj_sum = _pj_sum/3600
        _npj_sum_1m = _npj_sum_1m/3600
        _pj_sum_1m = _pj_sum_1m/3600
        _npj_sum_3m = _npj_sum_3m/3600
        _pj_sum_3m = _pj_sum_3m/3600

        """资源池情况
        """
        _dot, _spent_doing_sum = calTaskIndByDate('spent_doing', st_date, ed_date)
        __dot, _spent_done_sum = calTaskIndByDate('spent_done', st_date, ed_date)
        _org_dot, _doing_sum = calTaskIndByDate('doing', st_date, ed_date)
        _pd_sum = _spent_doing_sum+_spent_done_sum-_pj_sum-_npj_sum

        _dot_1m, _spent_doing_sum_1m = calTaskIndByDate('spent_doing', _st_date_1m, _ed_date_1m)
        __dot, _spent_done_sum_1m = calTaskIndByDate('spent_done', _st_date_1m, _ed_date_1m)
        _org_dot_1m, _doing_sum_1m = calTaskIndByDate('doing', _st_date_1m, _ed_date_1m)

        print(">>> _pd_sum_1m: %d,%d,%d,%d" % (_spent_done_sum_1m, _spent_doing_sum_1m, _pj_sum_1m, _npj_sum_1m))
        _pd_sum_1m = _spent_doing_sum_1m+_spent_done_sum_1m-_pj_sum_1m-_npj_sum_1m

        _dot_3m, _spent_doing_sum_3m = calTaskIndByDate('spent_doing', _st_date_3m, _ed_date_3m)
        __dot_3m, _spent_done_sum_3m = calTaskIndByDate('spent_done', _st_date_3m, _ed_date_3m)
        _org_dot_3m, _doing_sum_3m = calTaskIndByDate('doing', _st_date_3m, _ed_date_3m)
        _pd_sum_3m = _spent_doing_sum_3m+_spent_done_sum_3m-_pj_sum_3m-_npj_sum_3m

        context = dict(
            user={"role": role.level},
            total=pdPersonals.getNumbOfMember() +
                  pjPersonals.getNumbOfMember() +
                  rdmPersonals.getNumbOfMember(),
            total_task=pdPersonals.getTotalNumbOfTask() +
                       pjPersonals.getTotalNumbOfTask() +
                       rdmPersonals.getTotalNumbOfTask(),
            total_worklog=pdPersonals.getTotalNumbOfWorkLog() +
                          pjPersonals.getTotalNumbOfWorkLog() +
                          rdmPersonals.getTotalNumbOfWorkLog(),
            total_pj=len(pj),
            total_material=_count,
            ext_personals_stat=_ext_personals_stat,
            ext_personals=handler.get_project_info('ext_personals_t'),
            ext_personals_count=int(float(handler.get_sum(_ext_personals_stat, u'已解决'))/2.),
            pd_count=pdPersonals.getNumbOfMember(),
            pj_count=pjPersonals.getNumbOfMember(),
            rdm_count=rdmPersonals.getNumbOfMember(),
            pd_project=_project,
            sorted=sorted,
            task_ind_pd=echart_handler.effectscatterByInd('产品研发资源的当前负载执行情况',
                                                          _dot['pd'],
                                                          size={'width': 860, 'height': 220}),
            task_ind_pj=echart_handler.effectscatterByInd('项目开发资源的当前负载执行情况',
                                                          _dot['pj'],
                                                          size={'width': 860, 'height': 180}),
            task_ind_rdm=echart_handler.effectscatterByInd('测试资源的当前负载执行情况',
                                                           _dot['rdm'],
                                                           size={'width': 860, 'height': 120}),
            task_ind_pd_org=echart_handler.effectscatterByInd('产品研发资源的当前分配负载情况',
                                                              _org_dot['pd'],
                                                              size={'width': 860, 'height': 240}),
            task_ind_pj_org=echart_handler.effectscatterByInd('项目开发资源的当前分配负载情况',
                                                              _org_dot['pj'],
                                                              size={'width': 860, 'height': 180}),
            task_ind_rdm_org=echart_handler.effectscatterByInd('测试资源的当前分配负载情况',
                                                               _org_dot['rdm'],
                                                               size={'width': 860, 'height': 120}),
            task_pd=_pd_sum,
            task_pj=_pj_sum,
            task_npj=_npj_sum,
            task_pd_ratio="%0.2f" % (float(_pd_sum*100)/float(_pd_sum+_pj_sum+_npj_sum)),
            task_pj_ratio="%0.2f" % (float(_pj_sum*100)/float(_pd_sum+_pj_sum+_npj_sum)),
            task_npj_ratio="%0.2f" % (float(_npj_sum*100)/float(_pd_sum+_pj_sum+_npj_sum)),
            task_ratio=echart_handler.pie(u'年度工时占比（工时）',
                                          [u'产品研发', u'项目投入', u'其它'],
                                          [[_pd_sum,
                                            _pj_sum,
                                            _npj_sum]]
                                          ),
            task_pd_1m=_pd_sum_1m,
            task_pj_1m=_pj_sum_1m,
            task_npj_1m=_npj_sum_1m,
            task_pd_ratio_1m="%0.2f" % (float(_pd_sum_1m * 100) / float(_pd_sum_1m + _pj_sum_1m + _npj_sum_1m)),
            task_pj_ratio_1m="%0.2f" % (float(_pj_sum_1m * 100) / float(_pd_sum_1m + _pj_sum_1m + _npj_sum_1m)),
            task_npj_ratio_1m="%0.2f" % (float(_npj_sum_1m * 100) / float(_pd_sum_1m + _pj_sum_1m + _npj_sum_1m)),
            task_ratio_1m=echart_handler.pie(u'上个月工时占比（工时）',
                                          [u'产品研发', u'项目投入', u'其它'],
                                          [[_pd_sum_1m,
                                            _pj_sum_1m,
                                            _npj_sum_1m]]
                                          ),
            task_pd_3m=_pd_sum_3m,
            task_pj_3m=_pj_sum_3m,
            task_npj_3m=_npj_sum_3m,
            task_pd_ratio_3m="%0.2f" % (float(_pd_sum_3m * 100) / float(_pd_sum_3m + _pj_sum_3m + _npj_sum_3m)),
            task_pj_ratio_3m="%0.2f" % (float(_pj_sum_3m * 100) / float(_pd_sum_3m + _pj_sum_3m + _npj_sum_3m)),
            task_npj_ratio_3m="%0.2f" % (float(_npj_sum_3m * 100) / float(_pd_sum_3m + _pj_sum_3m + _npj_sum_3m)),
            task_ratio_3m=echart_handler.pie(u'近三个月工时占比（工时）',
                                          [u'产品研发', u'项目投入', u'其它'],
                                          [[_pd_sum_3m,
                                            _pj_sum_3m,
                                            _npj_sum_3m]]
                                          )
        )
    else:
        context = dict(
            user={"role": role.level},
            total=pdPersonals.getNumbOfMember() + pjPersonals.getNumbOfMember() + rdmPersonals.getNumbOfMember(),
            pd_count=pdPersonals.getNumbOfMember(),
            pj_count=pjPersonals.getNumbOfMember(),
            rdm_count=rdmPersonals.getNumbOfMember(),
            total_task=pdPersonals.getTotalNumbOfTask() +
                       pjPersonals.getTotalNumbOfTask() +
                       rdmPersonals.getTotalNumbOfTask(),
            total_worklog=pdPersonals.getTotalNumbOfWorkLog() +
                          pjPersonals.getTotalNumbOfWorkLog() +
                          rdmPersonals.getTotalNumbOfWorkLog(),
            total_pj=len(pj),
            total_material=_count,
            ext_personals_stat=_ext_personals_stat,
            ext_personals=handler.get_project_info('ext_personals_t'),
            ext_personals_count=int(float(handler.get_sum(_ext_personals_stat, u'已解决'))/2.),
        )

    return context


def set_pding_context():

    pd = handler.get_producting_list()
    context = dict(
        products=pd,
    )

    return context


def cal_ext_task_desc():
    """
    统计入侵任务信息
    :return: 统计结果
    """
    global extTask

    _stat = {'count': 0, 'spent': 0}
    if extTask is None:
        return _stat
    for _t in extTask:
        _stat['spent'] += _t['spent_time']

    _stat['count'] = len(extTask)

    return _stat


def set_context():

    global Personals, pdPersonals, pjPersonals, rdmPersonals, pd_databases,\
        pj_databases, rdm_databases, st_date, ed_date, today, extTask

    today = datetime.date.today()
    ed_date = today.strftime("%Y-%m-%d")

    extTask = handler.scan_pj_task(st_date, ed_date)

    pdPersonals.setDate(date={'st_date': '2018-01-01', 'ed_date': ed_date}, whichdate="updated")
    for _db in pd_databases:
        pdPersonals.scanProject(_db, u'产品研发中心')
    pdPersonals.calWorkInd()

    pjPersonals.setDate(date={'st_date': '2018-01-01', 'ed_date': ed_date}, whichdate="updated")
    for _db in pj_databases:
        pjPersonals.scanProject(_db, u'项目开发')
    pjPersonals.calWorkInd()

    rdmPersonals.setDate(date={'st_date': '2018-01-01', 'ed_date': ed_date}, whichdate="updated")
    for _db in rdm_databases:
        rdmPersonals.scanProject(_db, u'研发管理与测试部')
    rdmPersonals.calWorkInd()

    _checkon_am_data, _checkon_pm_data, _checkon_work, _checkon_user, _total_work_hour = handler.getChkOn(st_date, ed_date)
    _act_user = 0
    for _v in _checkon_user:
        if _checkon_user[_v] > 0:
            _act_user += 1

    # 项目统计信息
    _pj_count, _pj_op, _pj_ed, _pj_ing = handler.get_pj_state()
    pjStat = {
        "total": _pj_count,
        "op": _pj_op,
        "done": _pj_ed,
        "ing": _pj_ing,
        "pre": _pj_count-_pj_ing-_pj_ed-_pj_op,
    }
    _contract_count, _contract_total = handler.get_contract_stat()
    _budget, _budget_list = handler.get_budget_stat()
    contractStat = {
        "count": _contract_count,
        "total": "%0.2f" % _contract_total,
        "budget": "%0.2f" % (_budget / 10000.),
        "budgeted": 0,
    }

    # 产品统计信息
    _pd_count, _pd_ing, _deliver, _deliver_count = handler.get_product_stat()
    pdStat = {
        "total": _pd_count,
        "ing": _pd_ing,
        "deliver": _deliver,
        "count": _deliver_count,
    }

    _date_scale = pd.date_range(start='2018-01-01 00:00:00',
                                end='%s-%s-%s 23:59:59' % (today.year, today.month, today.day),
                                freq='1D')
    pydate_array = _date_scale.to_pydatetime()
    date_only_array = np.vectorize(lambda s: s.strftime('%Y-%m-%d'))(pydate_array)
    _date_scale = pd.Series(date_only_array)

    # 资源统计信息
    persion, date, _hr_month_date = handler.get_hr_stat(st_date, ed_date)
    _cost = 0
    for _p in persion:
        _cost += persion[_p]

    _persion_cost = _cost/3600

    pd_count, pd_cost, pd_n_cost = handler.get_pd4pj_stat(st_date, ed_date)
    _pj_task_stat = cal_ext_task_desc()
    count, done_count, persion, date, cost, g_stat = handler.get_task_stat(st_date, ed_date)

    hrStat = {
        "cost_time": _persion_cost,
        "cost": "%0.2f" % (float(_persion_cost) * 2.5/(26. * 8.)),
        "pd_count": pd_count,
        "pd_cost_time": pd_cost,
        "pd_cost": "%0.2f" % (float(pd_cost) * 2.5 / (26. * 8.)),
        "pd_n_cost_time": pd_n_cost,
        "pd_n_cost": "%0.2f" % (float(pd_n_cost) * 2.5 / (26. * 8.)),
        "pd_cost_total": "%0.2f" % (float(pd_cost+pd_n_cost) * 2.5 / (26. * 8.)),
        "pd_cost_time_total": pd_cost + pd_n_cost,
        "pd_pj_task_numb": _pj_task_stat['count'],
        "pd_pj_time": "%0.2f" % (_pj_task_stat['spent'] / 3600.),
        "pd_pj_task_numb_ratio": "%0.2f" % (_pj_task_stat['count']*100./g_stat['pd'][0]),
        "pd_pj_time_ratio": "%0.2f" % ((_pj_task_stat['spent'] / 3600.)*100./g_stat['pd'][2]),
    }

    _persion = []
    _persion_max = 0
    for _p in persion:
        _val = persion[_p]
        if _val > _persion_max:
            _persion_max = _val
        _persion.append(_val)

    _date = []
    for _d in _date_scale:
        if _d in date:
            _date.append(date[_d])
        else:
            _date.append(0)

    _ration = (float(len(persion))/float(_act_user))
    hrStat['ratio'] = "%0.2f" % (float(cost)*100./(_total_work_hour*_ration))

    # 任务统计
    taskStat = {
        "total": count,
        "persion_count": pdPersonals.getNumbOfMember() +
                         pjPersonals.getNumbOfMember() +
                         rdmPersonals.getNumbOfMember(),
        "persion_ratio": "%0.2f" % (float(len(persion)*100)/float(_act_user)),
        "done": done_count,
        "cost_time": "%0.2f" % cost,
        "cost_base": "2.5",
        "cost": "%0.2f" % (float(cost) * 2.5/(26. * 8.)),
        "ratio": "%0.2f" % (float(done_count*100)/float(count)),

        "pd_count": g_stat['pd'][0],
        "pd_persion": pdPersonals.getNumbOfMember(), # g_stat['pd'][1],
        "pd_cost_time": "%0.2f" % g_stat['pd'][2],
        "pd_cost": "%0.2f" % (float(g_stat['pd'][2]) * 2.5 / (26. * 8.)),

        "pj_group": "甘孜、嘉兴、四川公安等",
        "pj_count": g_stat['pj'][0],
        "pj_persion": pjPersonals.getNumbOfMember(), # g_stat['pj'][1],
        "pj_cost_time": "%0.2f" % g_stat['pj'][2],
        "pj_cost": "%0.2f" % (float(g_stat['pj'][2]) * 2.5 / (26. * 8.)),

        "rdm_count": g_stat['rdm'][0],
        "rdm_persion": rdmPersonals.getNumbOfMember(),
        "rdm_cost_time": "%0.2f" % g_stat['rdm'][2],
        "rdm_cost": "%0.2f" % (float(g_stat['rdm'][2]) * 2.5 / (26. * 8.)),

        "count_total": g_stat['pd'][0]+g_stat['pj'][0]+g_stat['rdm'][0],
        "persion_total": g_stat['pd'][1]+g_stat['pj'][1]+g_stat['rdm'][1],
        "cost_time_total": "%0.2f" % (g_stat['pd'][2]+g_stat['pj'][2]+g_stat['rdm'][2]),
        "cost_total": "%0.2f" % (float(g_stat['pd'][2]+g_stat['pj'][2]+g_stat['rdm'][2]) * 2.5 / (26. * 8.)),

    }

    _cost_loan, _trip_month_cost = handler.get_loan_stat(st_date, ed_date)
    _cost_reim, _reim_month_cost = handler.get_reimbursement_stat(st_date, ed_date)
    _cost_ticket, _addr_data, _month_date, _month_cost = handler.get_ticket_stat(st_date, ed_date)
    _trip_addr_data, _trip_month_data = handler.get_trip_data(st_date, ed_date)
    _reim_addr_data, _reim_month_data = handler.get_reim_data(st_date, ed_date)
    # 差旅统计信息
    tripStat = {
        "total": handler.get_trip_count(st_date, ed_date),
        "loan": "%0.2f" % (_cost_loan/10000.),
        "reim": "%0.2f" % (_cost_reim/10000.),
        "ticket": "%0.2f" % (_cost_ticket/10000.),
        "totalcost": "%0.2f" % ((_cost_loan+_cost_ticket)/10000.)
    }

    # 考勤信息
    checkStat = {
        "total": len(_checkon_user),
        "ratio": "%0.2f" % (float(_act_user)*100./len(_checkon_user)),
        "actUser": _act_user,
        "workHour": _total_work_hour,
        "workHourCost": "%0.2f" % (_total_work_hour*2.5/(26.*8.)),
    }

    role = Role.query.filter_by(name=current_user.username).first()
    print(">>> role.level = %d" % role.level)
    context = dict(
        report={"started_at": st_date, "ended_at": ed_date},
        user={"role": role.level},
        pjStat=pjStat,
        contractStat=contractStat,
        pdStat=pdStat,
        hrStat=hrStat,
        taskStat=taskStat,
        tripStat=tripStat,
        checkStat=checkStat,
        planeTicket=echart_handler.get_geo(u"航程", u"数据来源于携程", _addr_data),
        hrMonth=echart_handler.bar(u'任务', month, [{'title': u'个数', 'data': _hr_month_date}]),
        tripMonth=echart_handler.bar(u'申请', month,
                                     [{'title': u'人次', 'data': _trip_month_data},
                                      {'title': u'借款金额（1000元）', 'data': _trip_month_cost}]),
        reimMonth=echart_handler.bar(u'报账', month,
                                     [{'title': u'人次', 'data': _reim_month_data},
                                      {'title': u'报账金额（1000元）', 'data': _reim_month_cost}]),
        planeMonth=echart_handler.bar(u'航程', month,
                                      [{'title': u'航次', 'data': _month_date},
                                       {'title': u'金额（1000元）', 'data': _month_cost}]),
        trip=echart_handler.get_geo(u"借款", u"信息来源于出差申请", _trip_addr_data),
        reim=echart_handler.get_geo(u"报账", u"信息来源于差旅报账申请", _reim_addr_data),
        persionTask=echart_handler.scatter(u'任务/人', [0, _persion_max/2], _persion),
        dateTask=echart_handler.scatter(u'任务/天', [0, _persion_max/2], _date),
        chkonam=echart_handler.scatter(u'上班时间', [0,12], _checkon_am_data),
        chkonpm=echart_handler.scatter(u'下班时间', [8,24], _checkon_pm_data),
        chkonwork=echart_handler.scatter(u'工作时长', [0, 12], _checkon_work),
    )
    return context
