#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
#
#   Python服务程序集
#   ================
#   2018.5.9 @Chengdu
#
#   2018.5.16 @成都
#   1）明确本程序用于建立“公司”最基本的（原始的）信息。
#   2）后续的分析类数据，通过REST-API方式获取
#
#

from __future__ import unicode_literals

import mongodb_class
import MySQLdb
import mysql_hdr
import types
import datetime
import sys
import PersonalStat
from echart_handler import pie
import logging


reload(sys)
sys.setdefaultencoding('utf-8')
print sys.getdefaultencoding()

mongo_db = mongodb_class.mongoDB()
db = MySQLdb.connect(host="172.16.60.2", user="tk", passwd="53ZkAuoDVc8nsrVG", db="nebula", charset='utf8')
mysql_db = mysql_hdr.SqlService(db)

"""项目状态："""
pj_state = [u'在建', u'验收', u'交付', u'发布', u'运维']

pj_list = ['GZ', 'JX', 'SCGA', 'FT']
rdm_list = ['RDM', 'TESTCENTER']
pd_list = ['CPSJ', 'FAST', 'HUBBLE', 'ROOOT']


def get_trip_count(st_date, ed_date):
    """
    获取差旅记录个数
    :return:
    """

    # 从出差申请表中获取出差类型为：出差的数据
    return (get_table_count('trip_req', {u'外出类型': u'出差',
                                         "$and": [{u"审批完成时间": {"$gte": "%s" % st_date}},
                                                  {u"审批完成时间": {"$lt": "%s" % ed_date}}]}))

def addr_filter(addr_data, addr_info):
    """
    地址合规性处理
    :parameter addr_data：输出的地址数据
    :parameter addr_info：地址
    :return:
    """

    # 清洗数据，获取出差地址
    _addr = addr_info.split(' ')
    if len(_addr) == 1:
        _addr = addr_info.split(u'、')
    if len(_addr) == 1:
        _addr = addr_info.split(';')
    if len(_addr) == 1:
        _addr = addr_info.split(u'到')
    if len(_addr) == 1:
        _addr = addr_info.split('-')
    if len(_addr) == 1:
        _addr = addr_info.split('_')
    if len(_addr) == 1:
        _addr = addr_info.split('～')
    if len(_addr) == 1:
        _addr = addr_info.split('－')
    if len(_addr) == 1:
        _addr = addr_info.split('，')
    if len(_addr) == 1:
        _addr = addr_info.split('~')
    if len(_addr) == 1:
        _addr = addr_info.split('至')
    if len(_addr) == 1:
        _addr = addr_info.split('…')
    if len(_addr) == 1:
        _addr = addr_info.split('—')
    if len(_addr) == 1:
        if _addr[0] == u'上海嘉兴':
            _addr = [u"上海", u"嘉兴"]
        if _addr[0] == u'成都上海':
            _addr = [u"成都", u"上海"]
        if _addr[0] == u'成都康定':
            _addr = [u"成都", u"康定"]
        if _addr[0] == u'广西南宁':
            _addr = [u"南宁"]
        if _addr[0] == u'甘孜康定':
            _addr = [u"康定"]
        if _addr[0] == u'甘孜州康定':
            _addr = [u"康定"]
        if _addr[0] == u'天津石家庄上海':
            _addr = [u"天津", u"石家庄", u"上海"]
        if _addr[0] == u'甘孜州公安局':
            _addr = [u"康定"]

    for __addr in _addr:

        # 去掉空格信息
        __addr = __addr.replace(' ', ''). \
            replace(u'康定', ''). \
            replace(u'自贡', ''). \
            replace(u'理塘', ''). \
            replace(u'北川', ''). \
            replace(u'深证', '深圳'). \
            replace(u'甘孜', '康定'). \
            replace(u'广西南宁', '南宁'). \
            replace(u'从', ''). \
            replace(u'治安', ''). \
            replace(u'办公室', ''). \
            replace(u'三峡博物馆', ''). \
            replace(u'最高人民法院', ''). \
            replace(u'，再', ''). \
            replace(u'卫士通', ''). \
            replace(u'联通大厦', ''). \
            replace(u'四川省公安厅', u'成都'). \
            replace(u'四川公安厅', u'成都'). \
            replace(u'市', '')
        if len(__addr) < 2:
            continue
        if (__addr[0] == u'（') or (u'延续' in __addr):
            continue

        if __addr not in addr_data:
            addr_data[__addr] = 1
        else:
            addr_data[__addr] += 1

    return addr_data


def get_trip_data(st_date, ed_date):
    """
    获取差旅数据，在地图上展示。
    2018.5.16：按月份统计申请人次。
    :param mongo_db: 数据源
    :return:
    """

    addr_data = {}
    _month_stat = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0, "11": 0, "12": 0}

    # 从出差申请表中获取出差类型为：出差的数据
    mongo_db.connect_db('ext_system')
    _rec = do_search('trip_req', {u'外出类型': u'出差',
                                  "$and": [{u"审批完成时间": {"$gte": "%s" % st_date}},
                                           {u"审批完成时间": {"$lt": "%s" % ed_date}}]})

    for _r in _rec:
        addr_data = addr_filter(addr_data, _r[u'起止地点'])
        _date = datetime.datetime.strptime(_r[u'审批发起时间'], "%Y-%m-%d %H:%M:%S")
        _month_stat[str(_date.month)] += 1

    # 关闭数据库
    mongo_db.close_db()

    # print _month_stat
    _date = []
    for _d in range(1, 13):
        _date.append(_month_stat[str(_d)])

    print _date

    return addr_data, _date


def get_reim_data(st_date, ed_date):
    """
    获取差旅报账，在地图上展示。
    2018.5.16：按月份统计申请人次。
    :param mongo_db: 数据源
    :return:
    """

    addr_data = {}
    _month_stat = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0, "11": 0, "12": 0}

    # 从出差申请表中获取出差类型为：出差的数据
    mongo_db.connect_db('ext_system')
    _rec = do_search('reimbursement_req', {"$and": [{u"审批发起时间": {"$gte": "%s" % st_date}},
                                                    {u"审批发起时间": {"$lt": "%s" % ed_date}}]})

    for _r in _rec:
        addr_data = addr_filter(addr_data, _r[u'出差起止地点'])
        _date = datetime.datetime.strptime(_r[u'审批发起时间'], "%Y-%m-%d %H:%M:%S")
        _month_stat[str(_date.month)] += 1

    # 关闭数据库
    mongo_db.close_db()

    # print _month_stat
    _date = []
    for _d in range(1, 13):
        _date.append(_month_stat[str(_d)])

    print _date

    return addr_data, _date


def calHour(_str):
    """
    将时间字符串（HH:MM）转换成工时
    :param _str: 时间字符串
    :return: 工时数（2位小数）
    """
    ret = None
    _s = _str.split(':')
    try:
        if len(_s) == 2 and str(_s[0]).isdigit() and str(_s[1]).isdigit():
            _h = int(_s[0])
            _m = float("%.2f" % (int(_s[1])/60.))
            ret = _h + _m
    finally:
        return ret


def get_pj_state():

    _pj_op = 0
    _pj_done = 0
    _pj_ing = 0

    mongo_db.connect_db('ext_system')
    projects = do_search('project_t', {u'状态': {'$ne': u'挂起'}})
    _pj_count = projects.count()
    for _pj in projects:
        if _pj[u'状态'] in [u'在建', u'验收']:
            _pj_ing += 1
        elif _pj[u'状态'] == u'交付':
            _pj_done += 1
        elif _pj[u'状态'] == u'运维':
            _pj_op += 1

    mongo_db.close_db()

    return _pj_count, _pj_op, _pj_done, _pj_ing


def getChkOn(st_date, ed_date):
    """
    获取员工上下班时间序列
    :param st_date: 起始时间
    :param ed_date: 结束时间
    :return: 到岗记录时间序列
    """
    _sql = 'select KQ_AM, KQ_PM, KQ_NAME from checkon_t' \
           ' where str_to_date(KQ_DATE,"%%y-%%m-%%d") between "%s" and "%s"' % (st_date, ed_date)
    _res = mysql_db.do(_sql)

    _total_work_hour = 0.
    _seq_am = ()
    _seq_pm = ()
    _seq_work = ()
    _user = {}
    for _row in _res:

        if _row[2] not in _user:
            _user[_row[2]] = 0

        if (_row[0] == '#') or (_row[1] == '#'):
            continue
        _h = calHour(_row[0])
        if (_h is None) or (_h > 12.) or (_h < 6.):
            _h = 9.0
            _seq_am = _seq_am + (9.0,)
        else:
            _seq_am = _seq_am + (_h,)

        _h1 = calHour(_row[1])
        if (_h1 is None) or (_h1 < 12.):
            _h1 = 17.5
            _seq_pm = _seq_pm + (17.5,)
        else:
            _seq_pm = _seq_pm + (_h1,)

        _seq_work = _seq_work + ((_h1 - _h - 1.0),)
        _total_work_hour += (_h1 - _h - 1.0)

        _user[_row[2]] += 1

    return _seq_am, _seq_pm, _seq_work, _user, _total_work_hour


def get_task_stat(st_date, ed_date):

    _count = 0
    _done_count = 0
    personal = {}
    date = {}
    _cost = 0

    for pj in pd_list:
        mongo_db.connect_db(pj)
        _rec = mongo_db.handler('issue', 'find', {"issue_type": {"$ne": ["epic", "story"]},
                                                  "$and": [{"created": {"$gte": "%s" % st_date}},
                                                           {"created": {"$lt": "%s" % ed_date}}]})
        for _r in _rec:
            _count += 1
            if _r['status'] == u'完成':
                _done_count += 1
            if _r['users'] not in personal:
                personal[_r['users']] = 0
            personal[_r['users']] += 1
            _date = _r['created'].split('T')[0]
            if _date not in date:
                date[_date] = 0
            date[_date] += 1
            if _r['spent_time'] is not None:
                _cost += float(_r['spent_time'])/3600.

        mongo_db.close_db()

    _pd_count = _count
    _pd_personal = len(personal)
    _pd_cost = _cost

    for pj in pj_list:
        mongo_db.connect_db(pj)
        _rec = mongo_db.handler('issue', 'find', {"issue_type": {"$ne": ["epic", "story"]},
                                                  "$and": [{"created": {"$gte": "%s" % st_date}},
                                                           {"created": {"$lt": "%s" % ed_date}}]})
        for _r in _rec:
            _count += 1
            if _r['status'] == u'完成':
                _done_count += 1
            if _r['users'] not in personal:
                personal[_r['users']] = 0
            personal[_r['users']] += 1
            _date = _r['created'].split('T')[0]
            if _date not in date:
                date[_date] = 0
            date[_date] += 1
            if _r['spent_time'] is not None:
                _cost += float(_r['spent_time'])/3600.

        mongo_db.close_db()

    _pj_count = _count - _pd_count
    _pj_personal = len(personal) - _pd_personal
    _pj_cost = _cost - _pd_cost

    for pj in rdm_list:
        mongo_db.connect_db(pj)
        _rec = mongo_db.handler('issue', 'find', {"issue_type": {"$ne": ["epic", "story"]},
                                                  "$and": [{"created": {"$gte": "%s" % st_date}},
                                                           {"created": {"$lt": "%s" % ed_date}}]})
        for _r in _rec:
            _count += 1
            if _r['status'] == u'完成':
                _done_count += 1
            if _r['users'] not in personal:
                personal[_r['users']] = 0
            personal[_r['users']] += 1
            _date = _r['created'].split('T')[0]
            if _date not in date:
                date[_date] = 0
            date[_date] += 1
            if _r['spent_time'] is not None:
                _cost += float(_r['spent_time'])/3600.

        mongo_db.close_db()

    _rdm_count = _count - _pd_count - _pj_count
    _rdm_personal = len(personal) - _pd_personal - _pj_personal
    _rdm_cost = _cost - _pd_cost - _pj_cost

    return _count, _done_count, personal, date, _cost,\
           {'pd': [_pd_count, _pd_personal, _pd_cost],
            'pj': [_pj_count, _pj_personal, _pj_cost],
            'rdm': [_rdm_count, _rdm_personal, _rdm_cost],
            }


def get_hr_stat(st_date, ed_date):

    _month_stat = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0, "11": 0, "12": 0}
    personal = {}
    date = {}

    for pj in pd_list+pj_list+rdm_list:
        mongo_db.connect_db(pj)
        _rec = mongo_db.handler('worklog', 'find', {"$and": [{"created": {"$gte": "%s" % st_date}},
                                                             {"created": {"$lt": "%s" % ed_date}}]})
        for _r in _rec:
            if 'author' not in _r:
                continue
            if _r['author'] not in personal:
                personal[_r['author']] = 0
            personal[_r['author']] += _r['timeSpentSeconds']
            _date = _r['created'].split('T')[0]
            if _date not in date:
                date[_date] = 0
            date[_date] += 1

            _date = datetime.datetime.strptime(_date, "%Y-%m-%d")
            _month_stat[str(_date.month)] += 1

        mongo_db.close_db()

    _date = []
    for _d in range(1, 13):
        _date.append(int(_month_stat[str(_d)]))

    return personal, date, _date


def get_loan_stat(st_date, ed_date):

    _month_cost_stat = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0, "11": 0, "12": 0}

    mongo_db.connect_db('ext_system')
    _rec = do_search('loan_req', {"$and": [{u"审批完成时间": {"$gte": "%s" % st_date}},
                                           {u"审批完成时间": {"$lt": "%s" % ed_date}}]})
    _cost = 0.
    for _r in _rec:
        _cost += float(_r[u'金额小计'])

        _date = datetime.datetime.strptime(_r[u'审批完成时间'], "%Y-%m-%d %H:%M:%S")
        _month_cost_stat[str(_date.month)] += float(_r[u'金额小计'])

    mongo_db.close_db()

    _date_cost = []
    for _d in range(1, 13):
        _date_cost.append(int(_month_cost_stat[str(_d)]/1000.))

    return _cost, _date_cost


def get_reimbursement_stat(st_date, ed_date):

    _month_cost_stat = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0, "11": 0, "12": 0}

    mongo_db.connect_db('ext_system')
    _rec = do_search('reimbursement_req', {"$and": [{u"审批发起时间": {"$gte": "%s" % st_date}},
                                                    {u"审批发起时间": {"$lt": "%s" % ed_date}}]})
    _cost = 0.
    for _r in _rec:
        _cost += float(_r[u'金额小计'])

        _date = datetime.datetime.strptime(_r[u'审批发起时间'], "%Y-%m-%d %H:%M:%S")
        _month_cost_stat[str(_date.month)] += float(_r[u'金额小计'])

    mongo_db.close_db()

    _date_cost = []
    for _d in range(1, 13):
        _date_cost.append(int(_month_cost_stat[str(_d)]/1000.))

    return _cost, _date_cost


def get_ticket_stat(st_date, ed_date):

    _month_stat = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0, "11": 0, "12": 0}
    _month_cost_stat = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0, "11": 0, "12": 0}

    _date = st_date.split('-')
    _st_date = u"%d年%d月%d日" % (int(_date[0]), int(_date[1]), int(_date[2]))

    _date = ed_date.split('-')
    _ed_date = u"%d年%d月%d日" % (int(_date[0]), int(_date[1]), int(_date[2]))

    mongo_db.connect_db('ext_system')
    _rec = do_search('plane_ticket', {"$and": [{u"起飞时间": {"$gte": "%s" % _st_date}},
                                               {u"起飞时间": {"$lt": "%s" % _ed_date}}]})
    _cost = 0.
    addr_data = {}

    for _r in _rec:
        _cost += float(_r[u'实收'])

        # 出差地址
        _addr = _r[u'航程'].split('-')

        for __addr in _addr:

            # 去掉空格信息
            if len(__addr) < 2:
                continue

            if __addr not in addr_data:
                addr_data[__addr] = 1
            else:
                addr_data[__addr] += 1

        _date = datetime.datetime.strptime(_r[u'起飞时间'].replace(u'年', '-').replace(u'月', '-').replace(u'日', ""),
                                           u'%Y-%m-%d')
        _month_stat[str(_date.month)] += 1
        _month_cost_stat[str(_date.month)] += float(_r[u'实收'])

    mongo_db.close_db()

    _date = []
    for _d in range(1, 13):
        _date.append(int(_month_stat[str(_d)]))

    _date_cost = []
    for _d in range(1, 13):
        _date_cost.append(int(_month_cost_stat[str(_d)]/1000.))

    print _date, _date_cost

    return _cost, addr_data, _date, _date_cost


def is_pj(pj_info, summary):

    for _pj in pj_info:

        if _pj in (u'%s' % summary.replace(u'\xa0', u' ').replace(' ', '')).upper():
            return True

    return False


def get_pd4pj_stat(st_date, ed_date):

    pj_info = {}

    mongo_db.connect_db('ext_system')
    projects = do_search('project_t', {})

    for _pj in projects:
        if _pj[u'别名'] not in pj_info:
            pj_info[_pj[u'别名']] = [_pj[u'名称'], 0.]

    mongo_db.close_db()

    issues = []
    for _grp in ["CPSJ", "FAST", "ROOOT", "HUBBLE"]:

        """mongoDB数据库
        """
        mongo_db.connect_db(_grp)
        _search = {'issue_type': 'epic', 'summary': u'项目入侵'}
        _epic = mongo_db.handler('issue', 'find_one', _search)
        if _epic is None:
            continue

        _search = {'epic_link': _epic['issue'], 'status': u'完成',
                   "$and": [{"updated": {"$gte": "%s" % st_date}},
                            {"updated": {"$lte": "%s" % ed_date}}]}
        _cur = mongo_db.handler('issue', 'find', _search)
        for _issue in _cur:
            issues.append(_issue)

        mongo_db.close_db()

    _count = 0
    _pj_total_cost = 0.
    _npj_total_cost = 0.

    for _issue in issues:

        _it = 'spent_time'
        if type(_issue[_it]) is types.NoneType:
            continue

        _count += 1

        if not is_pj(pj_info, _issue['summary']):
            _npj_total_cost += (float(_issue['spent_time']) / 3600.)
            continue

        _pj_total_cost += (float(_issue['spent_time']) / 3600.)

    return _count, _pj_total_cost, _npj_total_cost


def get_product_stat():

    mongo_db.connect_db('ext_system')
    products = do_search('producting_t', {u"状态": {"$not": {"$eq": u"发布"}}})
    _ing_count = products.count()
    products = do_search('pd_shelves_t', {})
    _ed_count = products.count()

    _count = []
    _addr = []

    products = do_search('pd_deliver_t', {})
    for pd in products:
        if pd[u'安装地址'] not in _addr:
            _addr.append(pd[u'安装地址'])
        if pd[u'产品代号']+pd[u'版本'] not in _count:
            _count.append(pd[u'产品代号']+pd[u'版本'])

    mongo_db.close_db()

    return _ed_count, _ing_count, len(_addr), len(_count)


def get_contract_stat():

    mongo_db.connect_db('ext_system')
    contracts = do_search('contract_t', {})
    _count = contracts.count()
    _total = 0.
    for _r in contracts:
        if (len(_r[u'金额']) > 0) and ((_r[u'金额'].replace('.', '')).isdigit()):
            _total += float(_r[u'金额'])

    mongo_db.close_db()

    return _count, _total


def get_budget_stat():

    mongo_db.connect_db('ext_system')
    enginerrings = do_search('enginerring_budget', {})

    _total = {}
    _all = 0.
    for _r in enginerrings:
        if _r[u'项目编号'] not in _total:
            _total[u'项目编号'] = 0.

        if _r[u'金额'].replace(".", "").isdigit():
            _total[u'项目编号'] += float(_r[u'金额'])
            _all += float(_r[u'金额'])

    mongo_db.close_db()

    return _all, _total


def get_product_shelves():

    pd = []
    mongo_db.connect_db('ext_system')
    products = do_search('pd_shelves_t', {})

    for _pd in products:
        pd.append({'name': _pd[u'名称'],
                   'code': _pd[u'代号'],
                   'version': _pd[u'版本'],
                   'release': _pd[u'发布日期']})

    mongo_db.close_db()

    return pd


def get_product_deliver():
    """
    获取产品交付信息
    :return: 数据列表
    """

    pd = []
    mongo_db.connect_db('ext_system')
    products = do_search('pd_deliver_t', {})

    for _pd in products:
        if '-' in _pd[u'项目编号']:
            pj_name = search_one_table('project_t', {u'编号': _pd[u'项目编号']})
            if pj_name is None:
                _name = _pd[u'项目编号']
            else:
                _name = pj_name[u'名称']
        else:
            _name = '-'

        pd.append({'name': _name,
                   'code': _pd[u'产品代号'],
                   'version': _pd[u'版本'],
                   'address': _pd[u'安装地址'],
                   'date': _pd[u'交付日期']})

    mongo_db.close_db()

    return pd


def get_producting_list():
    """
    获取在研产品信息
    :return: 数据列表
    """

    pd = []
    mongo_db.connect_db('ext_system')
    products = do_search('producting_t', {u'状态': u'在研'})

    for _pd in products:
        pd.append({'name': _pd[u'名称'],
                   'code': _pd[u'代号'],
                   'version': _pd[u'版本'],
                   'date': _pd[u'发布日期']})
    mongo_db.close_db()
    return pd


def get_pd_project_desc(pd_code):
    """
    获取产品的研发项目信息
    :param pd_code: 产品代码
    :return: 数据列表
    """

    return search_one_table('pd_project_desc', {u'项目别名': u'%s' % pd_code.lower()})


def get_personal_stat(pd_code):
    """
    按产品获取人员的统计数据
    :param pd_code: 产品代码
    :return: 数据列表
    """
    mongo_db.connect_db('ext_system')
    return do_search('personal_stat', {u'别名': pd_code.lower()})


def get_project_info(table):
    """
    无条件获取表数据
    :param table: 表名
    :return: 数据列表
    """

    projects = []
    mongo_db.connect_db('ext_system')
    _pjs = mongo_db.handler(table, 'find', {})

    for _p in _pjs:
        projects.append(_p)

    return projects


def get_sum(values, field):
    """
    指定域值求和
    :param values: 数据集
    :param field: 指定域
    :return:
    """

    _sum = 0.
    for _v in values:
        if (field in dict(_v)) and (str(_v[field]).replace('.', '').isdigit()):
            _sum += float(_v[field])

    return "%0.2f" % _sum


def get_material():
    """
    获取项目归档数据
    :return:
    """

    mongo_db.connect_db('ext_system')
    return mongo_db.handler('material', 'find', {})


def do_search(table, search):
    """
    有条件获取表数据
    :param table: 表名
    :param search: 条件
    :return: 数据列表
    """
    return mongo_db.handler(table, "find", search)


def search_one_table(table, search):
    """
    有条件获取表数据
    :param table: 表名
    :param op: 操作方式
    :param search: 条件
    :return: 数据列表
    """
    return mongo_db.handler(table, "find_one", search)


def get_table_count(table, search):
    """
    有条件获取表数据记录个数
    :param table: 表名
    :param op: 操作方式
    :param search: 条件
    :return: 数据列表
    """
    return mongo_db.handler(table, "find", search).count()


def get_imp_projects():
    """
    获取2018年度重点项目执行情况
    :return:
    """
    pj_lists = {'JX': u'JX大数据',
                'GZ': u'GZ一号',
                'SCGA': u'SC综战1期',
                'FT': u'FT基础支撑平台',
                'HBB17': u'HBB 17课题',
                'BJXJC': u'BJ新机场',
                }
    _personal = PersonalStat.Personal()
    _pjs = []
    for _p in pj_lists:
        _pj_desc = {'name': pj_lists[_p]}
        _personal.clearData()
        _personal.scanProject(_p)
        if _personal.getNumbOfMember() == 0:
            logging.log(logging.WARN, ">>> project<%s> no personals" % _p)
            continue
        mongo_db.connect_db(_p)
        _pj_desc['personal_count'] = _personal.getNumbOfMember()
        _pj_desc['total_task'] = mongo_db.handler('issue', 'find', {}).count()
        _pj_desc['wait_task'] = mongo_db.handler('issue', 'find', {'status': u'待办'}).count()
        _pj_desc['done_task'] = mongo_db.handler('issue', 'find', {'status': u'完成'}).count()
        _pj_desc['pic'] = pie(_p, [u'等待', u'执行中', u'完成'],
                              [[_pj_desc['wait_task'],
                                _pj_desc['total_task']-_pj_desc['done_task'],
                                _pj_desc['done_task']]])
        _pjs.append(_pj_desc)

    return _pjs


def get_pj_managers():

    mongo_db.connect_db('ext_system')
    pj_managers = {}
    _lists = mongo_db.handler('pj_deliver_t', 'find', {})
    for _pj in _lists:
        if _pj[u'负责人'] not in pj_managers:
            pj_managers[_pj[u'负责人']] = []
        pj_managers[_pj[u'负责人']].append(_pj[u'项目名称'][_pj[u'项目名称'].find('(简称'):])

    return pj_managers


def scan_pj_task(st_date, ed_date):
    """
    获取产品研发中心投入到非产品研发的任务
    :param st_date: 起始时间
    :param ed_date: 截止时间
    :return: 数据
    """
    _task = []
    for _pd_g in pd_list:
        mongo_db.connect_db(_pd_g)
        _rec = mongo_db.handler('issue', 'find', {"issue_type": {"$ne": ["epic", "story"]},
                                                  "summary": {'$regex': ".*入侵.*"},
                                                  "spent_time": {'$ne': None},
                                                  "$and": [{"created": {"$gte": "%s" % st_date}},
                                                           {"created": {"$lt": "%s" % ed_date}}]})
        for _r in _rec:
            _task.append(_r)

        ext_epic = mongo_db.handler("issue", "find_one", {"issue_type": "epic", "summary": u"项目入侵"})
        _res = mongo_db.handler("issue", "find", {"issue_type": {"$ne": ["epic", "story"]},
                                                  "spent_time": {'$ne': None},
                                                  "epic_link": ext_epic['issue']})
        for _r in _res:
            if _r not in _task:
                _task.append(_r)

    return _task

