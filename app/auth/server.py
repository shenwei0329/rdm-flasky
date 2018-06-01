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

pd_databases = ['CPSJ', 'FAST', 'HUBBLE', 'ROOOOT']
pj_databases = ['JX', 'GZ', 'SCGA']
rdm_databases = ['RDM', 'TESTCENTER']

month = [u'一月', u'二月', u'三月', u'四月', u'五月', u'六月', u'七月', u'八月', u'九月', u'十月', u'十一月', u'十二月']

st_date = '2018-01-01'
ed_date = '2018-12-31'
pdPersonals = PersonalStat.Personal()
pjPersonals = PersonalStat.Personal()
rdmPersonals = PersonalStat.Personal()
Personals = []


def set_honor_context():
    _pd_work_ind = pdPersonals.getWorkIndList()
    _pj_work_ind = pjPersonals.getWorkIndList()
    _rdm_work_ind = rdmPersonals.getWorkIndList()

    _pd_count = 18
    _pd_numb_list = _pd_count/6
    """int(float(len(_pd_work_ind))*0.2 + 0.5)
    """
    _pj_count = 6
    _pj_numb_list = _pj_count/6
    """int(float(len(_pj_work_ind))*0.35 + 0.5)
    """
    _rdm_count = 6
    _rdm_numb_list = _rdm_count/6
    """int(float(len(_rdm_work_ind))*0.2 + 0.5)
    """

    logging.log(logging.WARN, ">>> %s,%s,%s" % (type(_pd_work_ind), type(_pj_work_ind), type(_rdm_work_ind)))
    logging.log(logging.WARN, ">>> %d,%d,%d" % (_pd_count, _pj_count, _rdm_count))

    _pd_list = []
    _pj_list = []
    _rdm_list = []

    for _i in range(_pd_numb_list):
        _personal = []
        for _j in range(6):
            _item = _pd_work_ind[_i*6 + _j]
            logging.log(logging.WARN, ">>> %s:%d" % (_item[0], _item[1]))
            _personal.append({'name': _item[0], 'quota': _item[1]})
        _pd_list.append(_personal)

    for _i in range(_pj_numb_list):
        _personal = []
        for _j in range(6):
            _item = _pj_work_ind[_i*6 + _j]
            logging.log(logging.WARN, ">>> %s:%d" % (_item[0], _item[1]))
            _personal.append({'name': _item[0], 'quota': _item[1]})
        _pj_list.append(_personal)

    for _i in range(_rdm_numb_list):
        _personal = []
        for _j in range(6):
            _item = _rdm_work_ind[_i*6 + _j]
            logging.log(logging.WARN, ">>> %s:%d" % (_item[0], _item[1]))
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


def set_rdm_context():

    global Personals, pdPersonals, pjPersonals, rdmPersonals

    role = Role.query.filter_by(name=current_user.username).first()

    pj = []
    _m = handler.get_material()
    _count = _m.count()
    for __m in _m:
        if __m[u'项目名称'] not in pj:
            pj.append(__m[u'项目名称'])

    _ext_personals_stat = handler.get_project_info('ext_personals_stat')
    context = dict(
        user={"role": role.level},
        total=len(Personals),
        total_task=pdPersonals.getTotalNumbOfTask() + pjPersonals.getTotalNumbOfTask() + rdmPersonals.getTotalNumbOfTask(),
        total_worklog=pdPersonals.getTotalNumbOfWorkLog() + pjPersonals.getTotalNumbOfWorkLog() + rdmPersonals.getTotalNumbOfWorkLog(),
        total_pj=len(pj),
        total_material=_count,
        ext_personals_stat=_ext_personals_stat,
        ext_personals=handler.get_project_info('ext_personals_t'),
        ext_personals_count=handler.get_sum(_ext_personals_stat, u'数量')
    )

    return context


def set_pding_context():

    pd = handler.get_producting_list()
    context = dict(
        products=pd,
    )

    return context


def set_context():

    global Personals, pdPersonals, pjPersonals, rdmPersonals, pd_databases, pj_databases, rdm_databases, st_date, ed_date, today

    today = datetime.date.today()
    ed_date = today.strftime("%Y-%m-%d")

    pdPersonals.setDate(date={'st_date': '2018-03-01', 'ed_date': ed_date})
    pjPersonals.setDate(date={'st_date': '2018-03-01', 'ed_date': ed_date})
    rdmPersonals.setDate(date={'st_date': '2018-03-01', 'ed_date': ed_date})

    """清空原有数据
    """
    pdPersonals.clearData()
    pjPersonals.clearData()
    rdmPersonals.clearData()


    for _db in pd_databases:
        pdPersonals.scanProject(_db)
    for _db in pj_databases:
        pjPersonals.scanProject(_db)
    for _db in rdm_databases:
        rdmPersonals.scanProject(_db)

    pdPersonals.calWorkInd()
    pjPersonals.calWorkInd()
    rdmPersonals.calWorkInd()

    for _p in [pdPersonals, pjPersonals, rdmPersonals]:
        for __p in _p.getNameList():
            if __p not in Personals:
                Personals.append(__p)

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
        "pre": _pj_count-_pj_ing-_pj_ed,
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
    }

    count, done_count, persion, date, cost, g_stat = handler.get_task_stat(st_date, ed_date)

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
        "persion_count": len(Personals),
        "persion_ratio": "%0.2f" % (float(len(persion)*100)/float(_act_user)),
        "done": done_count,
        "cost_time": "%0.2f" % cost,
        "cost_base": "2.5",
        "cost": "%0.2f" % (float(cost) * 2.5/(26. * 8.)),
        "ratio": "%0.2f" % (float(done_count*100)/float(count)),

        "pd_count": g_stat['pd'][0],
        "pd_persion": g_stat['pd'][1],
        "pd_cost_time": "%0.2f" % g_stat['pd'][2],
        "pd_cost": "%0.2f" % (float(g_stat['pd'][2]) * 2.5 / (26. * 8.)),

        "pj_group": "甘孜、嘉兴、四川公安等",
        "pj_count": g_stat['pj'][0],
        "pj_persion": g_stat['pj'][1],
        "pj_cost_time": "%0.2f" % g_stat['pj'][2],
        "pj_cost": "%0.2f" % (float(g_stat['pj'][2]) * 2.5 / (26. * 8.)),

        "rdm_count": g_stat['rdm'][0],
        "rdm_persion": g_stat['rdm'][1],
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
        persionTask=echart_handler.scatter(u'【人-任务】', [0, _persion_max/2], _persion),
        dateTask=echart_handler.scatter(u'【日期-任务】', [0, _persion_max/2], _date),
        chkonam=echart_handler.scatter(u'上班时间', [0,12], _checkon_am_data),
        chkonpm=echart_handler.scatter(u'下班时间', [8,24], _checkon_pm_data),
        chkonwork=echart_handler.scatter(u'工作时长', [0, 12], _checkon_work),
    )
    return context
