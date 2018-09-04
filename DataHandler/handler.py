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
#   2018.6.23 @成都
#   1）引入ConfigParser及配置文件
#   2）程序注释
#

from __future__ import unicode_literals

import mongodb_class
import MySQLdb
import mysql_hdr
import types
import datetime
import sys
import PersonalStat
from echart_handler import pie, bar_x
import logging
import ConfigParser
import os

reload(sys)
sys.setdefaultencoding('utf-8')
print sys.getdefaultencoding()

conf = ConfigParser.ConfigParser()
conf.read(os.path.split(os.path.realpath(__file__))[0] + '/rdm.cnf')

extTask = None

print(">>> MYSQL: %s,%s,%s" % (conf.get('MYSQL', 'host'), conf.get('MYSQL', 'user'), conf.get('MYSQL', 'password')))

mongo_db = mongodb_class.mongoDB()
db = MySQLdb.connect(host=conf.get('MYSQL', 'host'),
                     user=conf.get('MYSQL', 'user'),
                     passwd=conf.get('MYSQL', 'password'),
                     db="nebula",
                     charset='utf8')
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


def cal_hour(_str):
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
    """
    获取项目统计信息
    :return: 统计
    """
    _pj_op = 0
    _pj_done = 0
    _pj_ing = 0

    mongo_db.connect_db('ext_system')
    projects = do_search('project_t', {u'状态': {'$ne': u'挂起'}})
    _pj_count = len(projects)
    for _pj in projects:
        if _pj[u'状态'] in [u'在建', u'验收']:
            _pj_ing += 1
        elif _pj[u'状态'] == u'交付':
            _pj_done += 1
        elif _pj[u'状态'] == u'运维':
            _pj_op += 1

    mongo_db.close_db()

    return _pj_count, _pj_op, _pj_done, _pj_ing


def getChkOn(nWeek):
    """
    获取员工上下班时间序列
    :param nWeek: 近期周数
    :return: 到岗记录时间序列
    """
    _date = cal_date_weekly(nWeek)
    _sql = 'select KQ_AM, KQ_PM, KQ_NAME from checkon_t' \
           ' where str_to_date(KQ_DATE,"%%y-%%m-%%d") between "%s" and "%s"' % \
           (_date['st_date'], _date['ed_date'])

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
        _h = cal_hour(_row[0])
        if (_h is None) or (_h > 12.) or (_h < 6.):
            _h = 9.0
            _seq_am = _seq_am + (9.0,)
        else:
            _seq_am = _seq_am + (_h,)

        _h1 = cal_hour(_row[1])
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
    """
    获取任务统计信息
    :param st_date: 起始日期
    :param ed_date: 截止日期
    :return: 统计，包含产品研发、项目开发和研发管理与测试
    """
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
    """
    获取人力资源统计信息
    :param st_date: 起始日期
    :param ed_date: 截止日期
    :return: 统计
    """
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
    """
    获取差旅统计信息
    :param st_date: 起始日期
    :param ed_date: 截止日期
    :return: 统计
    """
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
    """
    获取报账统计
    :param st_date: 起始日期
    :param ed_date: 截止日期
    :return: 统计
    """
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
    """
    获取机票统计信息
    :param st_date: 起始日期
    :param ed_date: 截止日期
    :return: 统计值
    """
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
    """
    判断summary是否包含项目信息
    :param pj_info:
    :param summary:
    :return:
    """

    for _pj in pj_info:

        if _pj in (u'%s' % summary.replace(u'\xa0', u' ').replace(' ', '')).upper():
            return True

    return False


def get_pd4pj_stat(st_date, ed_date):
    """
    获取产品研发对外支撑投入的统计信息
    :param st_date: 起始日期
    :param ed_date: 截止日期
    :return: 统计值
    """

    issues = scan_pj_task(st_date, ed_date)

    pj_info = {}

    mongo_db.connect_db('ext_system')
    projects = do_search('project_t', {})

    for _pj in projects:
        if _pj[u'别名'] not in pj_info:
            pj_info[_pj[u'别名']] = [_pj[u'名称'], 0.]

    mongo_db.close_db()

    _count = 0
    _pj_total_cost = 0.
    _npj_total_cost = 0.

    for _issue in issues:
        """检索summary字段是否包含项目信息，以确定投入的项目明细
        """
        _it = 'spent_time'
        if type(_issue[_it]) is types.NoneType:
            continue

        _count += 1

        if not is_pj(pj_info, _issue['summary']):
            _npj_total_cost += (float(_issue['spent_time']) / 3600.)
            continue

        _pj_total_cost += (float(_issue['spent_time']) / 3600.)

    return _count, _pj_total_cost, _npj_total_cost


def get_test_center_stat(st_date, ed_date):
    """
    获取测试中心的统计信息
    :param st_date: 起始日期
    :param ed_date: 截止日期
    :return: 统计值
    """

    issues = scan_test_center_task(st_date, ed_date)

    pj_info = {}

    mongo_db.connect_db('ext_system')
    projects = do_search('project_t', {})

    for _pj in projects:
        if _pj[u'别名'] not in pj_info:
            pj_info[_pj[u'别名']] = [_pj[u'名称'], 0.]

    mongo_db.close_db()

    _count = 0
    _pj_total_cost = 0.
    _npj_total_cost = 0.

    for _issue in issues:
        """检索summary字段是否包含项目信息，以确定投入的项目明细
        """
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
    """
    获取产品统计信息
    :return: 已发布数、在研数、安装地的数量、交付产品总量
    """

    mongo_db.connect_db('ext_system')
    products = do_search('producting_t', {u"状态": {"$not": {"$eq": u"发布"}}})
    _ing_count = len(products)
    products = do_search('pd_shelves_t', {})
    _ed_count = len(products)

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
    """
    获取合同金额
    :return: 合同数、总计金额
    """
    mongo_db.connect_db('ext_system')
    contracts = do_search('contract_t', {})
    _count = len(contracts)
    _total = 0.
    for _r in contracts:
        if (len(_r[u'金额']) > 0) and ((_r[u'金额'].replace('.', '')).isdigit()):
            _total += float(_r[u'金额'])

    mongo_db.close_db()

    return _count, _total


def get_budget_stat():
    """
    获取项目预算统计
    :return: 统计值，含总计、每个项目的分项值
    """
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
    """
    获取产品货架内容
    :return: 货架上的产品列表
    """
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
    _value = []
    _cur = mongo_db.handler(table, "find", search)
    for _v in _cur:
        _value.append(_v)
    return _value


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
                'JTJD': u'金堂禁毒',
                'HZZ': u'河长制',
                'AH2': u'安徽2期',
                }
    _personal = PersonalStat.Personal()
    _pjs = []
    for _p in pj_lists:
        _pj_desc = {'name': pj_lists[_p]}
        _personal.clearData()
        _personal.scanProject(_p, u'项目开发', extTask)
        _pj_desc['personal_count'] = _personal.getNumbOfMember()
        _pj_desc['total_task'] = 0
        _pj_desc['wait_task'] = 0
        _pj_desc['done_task'] = 0
        _pj_desc['done_task'] = 0
        _pj_desc['done_task'] = 0
        _pj_desc['ratio'] = "0.00"
        mongo_db.connect_db('ext_system')
        _pj_desc['process'] = bar_x("",
                                    ["进度执行", "预算执行"],
                                    [mongo_db.handler('pj_doing', 'find', {u'项目简称': _p})[0][u'进度执行'],
                                     mongo_db.handler('pj_doing', 'find', {u'项目简称': _p})[0][u'预算执行']]
                                    )
        if _personal.getNumbOfMember() == 0:
            logging.log(logging.WARN, ">>> project<%s> no personals" % _p)
            _pjs.append(_pj_desc)
            continue
        mongo_db.connect_db(_p)
        _pj_desc['total_task'] = mongo_db.handler('issue', 'find', {}).count()
        _pj_desc['wait_task'] = mongo_db.handler('issue', 'find', {'status': u'待办'}).count()
        _pj_desc['done_task'] = mongo_db.handler('issue', 'find', {'status': u'完成'}).count()
        _pj_desc['done_task'] += mongo_db.handler('issue', 'find', {'status': u'已关闭'}).count()
        _pj_desc['done_task'] += mongo_db.handler('issue', 'find', {'status': u'已解决'}).count()
        _pj_desc['ratio'] = "%0.2f" % (float(_pj_desc['done_task'])/float(_pj_desc['personal_count']))
        _pj_desc['pic'] = pie(_p, [u'等待', u'执行中', u'完成'],
                              [[_pj_desc['wait_task'],
                                _pj_desc['total_task']-_pj_desc['done_task'],
                                _pj_desc['done_task']]])
        _pjs.append(_pj_desc)

    return _pjs


def get_pj_managers():
    """
    获取项目经理列表
    :return: 列表
    """
    mongo_db.connect_db('ext_system')
    pj_managers = {}
    _lists = mongo_db.handler('pj_deliver_t', 'find', {})
    for _pj in _lists:
        if _pj[u'负责人'] not in pj_managers:
            pj_managers[_pj[u'负责人']] = []
        pj_managers[_pj[u'负责人']].append(_pj[u'项目名称'][_pj[u'项目名称'].find('(简称'):])

    return pj_managers


def scan_pd_task(pd_name, st_date, ed_date):
    """
    扫描研发任务（排除外部支撑的）
    :param pd_name: 产品项目名称
    :param st_date: 起始日期
    :param ed_date: 截止日期
    :return: 任务列表
    """
    _pd_name = pd_name.upper()
    logging.log(logging.WARN, ">>> scan_pd_task.ext_date: <%s>: fr %s to %s" % (pd_name, st_date, ed_date))
    _task = []
    for _pd_g in pd_list:
        """从summary内容查找带有"入侵"的issue
        """
        if _pd_g not in ['CPSJ', 'ROOOT', _pd_name]:
            continue

        mongo_db.connect_db(_pd_g)
        ext_epic = mongo_db.handler("issue", "find_one", {"issue_type": "epic", "summary": u"项目入侵"})
        _rec = mongo_db.handler('issue', 'find', {"issue_type": {"$ne": ["epic", "story"]},
                                                  "spent_time": {'$ne': None},
                                                  "epic_link": {'$ne': ext_epic['issue']},
                                                  "$and": [{"updated": {"$gte": "%s" % st_date}},
                                                           {"updated": {"$lt": "%s" % ed_date}}]})
        for _r in _rec:
            if _r not in extTask:
                if _pd_g in ['CPSJ', 'ROOOT']:
                    if (_pd_name in _r['landmark']) or (_pd_name in _r['summary']):
                        _task.append(_r)
                else:
                    _task.append(_r)

    return _task


def scan_pj_task(st_date, ed_date):
    """
    获取产品研发中心投入到非产品研发的任务
    :param st_date: 起始时间
    :param ed_date: 截止时间
    :return: 数据
    """
    logging.log(logging.WARN, ">>> scan_pj_task.ext_date: fr %s to %s" % (st_date, ed_date))
    _task = []
    for _pd_g in pd_list:
        """从summary内容查找带有"入侵"的issue
        """
        mongo_db.connect_db(_pd_g)
        _rec = mongo_db.handler('issue', 'find', {"issue_type": {"$ne": ["epic", "story"]},
                                                  "summary": {'$regex': ".*入侵.*"},
                                                  "spent_time": {'$ne': None},
                                                  "$and": [{"created": {"$gte": "%s" % st_date}},
                                                           {"created": {"$lt": "%s" % ed_date}}]})
        logging.log(logging.WARN, ">>> ext_regex: %s-%d" % (_pd_g, _rec.count()))
        for _r in _rec:
            _task.append(_r)

        """查找"项目入侵"epic，然后查找epic_link属于该epic的issue
        """
        ext_epic = mongo_db.handler("issue", "find_one", {"issue_type": "epic", "summary": u"项目入侵"})
        _res = mongo_db.handler("issue", "find", {"issue_type": {"$ne": ["epic", "story"]},
                                                  "spent_time": {'$ne': None},
                                                  "$and": [{"created": {"$gte": "%s" % st_date}},
                                                           {"created": {"$lt": "%s" % ed_date}}],
                                                  "epic_link": ext_epic['issue']})
        logging.log(logging.WARN, ">>> ext_epic: %s-%d" % (_pd_g, _res.count()))
        for _r in _res:
            if _r not in _task:
                _task.append(_r)

    return _task


def scan_test_center_task(st_date, ed_date):
    """
    扫描测试中心的任务
    :param st_date: 起始日期
    :param ed_date: 截止日期
    :return: 任务列表
    """
    logging.log(logging.WARN, ">>> scan_test_center_task.ext_date: fr %s to %s" % (st_date, ed_date))
    _task = []

    mongo_db.connect_db("TESTCENTER")

    _rec = mongo_db.handler('issue', 'find', {"issue_type": u'任务',
                                              "spent_time": {'$ne': None},
                                              "$and": [{"updated": {"$gte": "%s" % st_date}},
                                                       {"updated": {"$lt": "%s" % ed_date}}]})
    for _r in _rec:
        _task.append(_r)
    return _task


def get_personal_by_level(lvl):
    """
    按职级获取人员列表
    :param lvl: 职级
    :return: 列表
    """

    mongo_db.connect_db('ext_system')
    return mongo_db.handler('pd_member_level_t', 'find', {u'职级': "%d" % lvl})


def xy_task_by_level(Personals):
    """
    各职级的执行任务情况
    :param Personals: 人员表
    :return: 数据，X：职级，Y：员工名称
    """

    x = []
    y = []

    _personals = Personals.getNameList()
    for _lvl in range(13):

        # print(">>> _lvl = %d" % _lvl)
        _ps = get_personal_by_level(_lvl)
        if _ps is None:
            continue

        for _p in _ps:
            if _p[u'姓名'] in _personals:
                x.append(_lvl)
                y.append(Personals.getNumbOfTask(_p[u'姓名']))

    return x, y


def xy_spent_time_by_level(Personals):
    """
    各职级的执行任务的用时情况
    :param Personals: 人员表
    :return: 数据，X：职级，Y：花费时间总计
    """

    x = []
    y = []

    _personals = Personals.getNameList()
    for _lvl in range(13):

        # print(">>> _lvl = %d" % _lvl)
        _ps = get_personal_by_level(_lvl)
        if _ps is None:
            continue

        for _p in _ps:
            if _p[u'姓名'] in _personals:
                _times = Personals.getSpentTime(_p[u'姓名'])
                for _t in _times:
                    if _t/3600 > 100:
                        continue
                    x.append(_lvl)
                    y.append(_t/3600.)

    return x, y


def xy_org_time_by_level(Personals):
    """
    各职级的执行任务的预估时间情况
    :param Personals: 人员表
    :return: 数据
    """

    x = []
    y = []

    _personals = Personals.getNameList()
    for _lvl in range(13):

        # print(">>> _lvl = %d" % _lvl)
        _ps = get_personal_by_level(_lvl)
        if _ps is None:
            continue

        for _p in _ps:
            if _p[u'姓名'] in _personals:
                _times = Personals.getOrgTime(_p[u'姓名'])
                for _t in _times:
                    if _t/3600 > 100:
                        continue
                    x.append(_lvl)
                    y.append(_t/3600.)

    return x, y


def xy_spent_time_sum_by_level(Personals):
    """
    各职级的执行任务的用时情况
    :param Personals: 人员表
    :return: 数据
    """

    x = []
    y = []

    _personals = Personals.getNameList()
    for _lvl in range(13):

        # print(">>> _lvl = %d" % _lvl)
        _ps = get_personal_by_level(_lvl)
        if _ps is None:
            continue

        for _p in _ps:
            if _p[u'姓名'] in _personals:
                _t = Personals.getSumSpentTime(_p[u'姓名'])
                x.append(_lvl)
                y.append(_t/3600.)

    return x, y


def xy_org_time_sum_by_level(Personals):
    """
    各职级的执行任务的预估时间情况
    :param Personals: 人员表
    :return: 数据
    """

    x = []
    y = []

    _personals = Personals.getNameList()
    for _lvl in range(13):

        # print(">>> _lvl = %d" % _lvl)
        _ps = get_personal_by_level(_lvl)
        if _ps is None:
            continue

        for _p in _ps:
            if _p[u'姓名'] in _personals:
                _t = Personals.getSumOrgTime(_p[u'姓名'])
                x.append(_lvl)
                y.append(_t/3600.)

    return x, y


def xy_diff_time_by_level(Personals):
    """
    各职级的执行任务的预估时间情况
    :param Personals: 人员表
    :return: 数据
    """

    x = []
    y = []

    _personals = Personals.getNameList()
    for _lvl in range(13):

        # print(">>> _lvl = %d" % _lvl)
        _ps = get_personal_by_level(_lvl)
        if _ps is None:
            continue

        for _p in _ps:
            if _p[u'姓名'] in _personals:
                _t = Personals.getDiffTime(_p[u'姓名'])
                x.append(_lvl)
                y.append(_t/3600.)

    return x, y


def cal_st_date(month, nMonth):
    """
    计算指定日期的前nMonth个月
    :param month: 指定的日期
    :param nMonth: 前几个月
    :return: 计算的日期
    """

    _m = month
    for _i in range(nMonth):
        _m = _m - datetime.timedelta(days=_m.day)
    return _m.replace(day=1)


def cal_date_weekly(nWeek):
    """
    计算月度日期
    :param nWeek: 指定是前几周，1：上周，2：前二周...
    :return: 起止日期
    """
    _now = datetime.datetime.now()
    _st_date = _now - datetime.timedelta(days=7*nWeek)
    _ed_date = _now.strftime("%Y-%m-%d")
    _st_date = _st_date.strftime("%Y-%m-%d")
    return {"st_date": _st_date, "ed_date": _ed_date}


def cal_date_monthly(nMonth):
    """
    计算月度日期
    :param nMonth: 指定是前几个月，1：上一个月，2：前二个月...
    :return: 起止日期
    """

    """上月最后一天"""
    _now = datetime.datetime.now()
    _ed_date = _now - datetime.timedelta(days=_now.day)
    _bg_date = _ed_date

    """起始日期"""
    _st_date = cal_st_date(_ed_date, nMonth-1).strftime("%Y-%m-%d")
    _ed_date = _ed_date.strftime("%Y-%m-%d")

    _month = []
    _month.append({'year': _bg_date.year, 'month': _bg_date.month})
    while is_date_aft(_bg_date.strftime("%Y-%m-%d"), _st_date):
        _m = _bg_date.month
        _y = _bg_date.year
        _val = {'month': _m, 'year': _y}
        if _val not in _month:
            _month.append(_val)
        # print("%s" % _month)
        _bg_date = _bg_date - datetime.timedelta(days=_bg_date.day)

    """获取排序的月份序列，用于生成sankey的nodes"""
    _month = sorted(_month)
    logging.log(logging.WARN, ">>> %s --> %s, %s" % (_st_date, _ed_date, _month))

    return {"st_date": _st_date, "ed_date": _ed_date, "month": _month}


def is_date_bef(dateA, dateB):
    """
    判断日期A是否在日期B前
    :param dateA: 日期A
    :param dateB: 日期B
    :return: 判断结果
    """
    # logging.log(logging.WARN,">>> is_date_bef dateA=%s, dateB=%s" % (dateA, dateB))
    _time1 = datetime.datetime.strptime(dateA, "%Y-%m-%d")
    _time2 = datetime.datetime.strptime(dateB, "%Y-%m-%d")
    return _time1 < _time2


def is_date_aft(dateA, dateB):
    """
    判断日期A是否在日期B后
    :param dateA: 日期A
    :param dateB: 日期B
    :return: 判断结果
    """
    # logging.log(logging.WARN,">>> is_date_aft dateA=%s, dateB=%s" % (dateA, dateB))
    _time1 = datetime.datetime.strptime(dateA, "%Y-%m-%d")
    _time2 = datetime.datetime.strptime(dateB, "%Y-%m-%d")
    return _time1 > _time2


def cal_one_month(year, month):
    """
    计算某年某个月份的日期
    :param year: 年份
    :param month: 月份
    :return: {'st_date': 起始日期, 'ed_date': 截止日期}
    """

    import calendar
    last_day = calendar.monthrange(year, month)[1]

    return {"st_date": "%d-%02d-01" % (year, month), "ed_date": "%d-%02d-%02d" % (year, month, last_day)}


def cal_one_month_by_finance(year, month):
    """
    计算某年某个月份的财务月统计日期，财务要求从上一月份10日起至本月10日前计算。
    :param year: 年份
    :param month: 月份
    :return: {'st_date': 起始日期, 'ed_date': 截止日期}
    """
    _day = int(conf.get('FINANCE', 'day'))
    if month == 1:
        return {"st_date": "%d-12-%02d" % (year-1, _day), "ed_date": "%d-%02d-%02d" % (year, month, _day)}
    else:
        return {"st_date": "%d-%02d-%02d" % (year, month-1, _day), "ed_date": "%d-%02d-%02d" % (year, month, _day)}


def cal_personal_checkon(personal, st_date, ed_date):
    """
    统计人员出勤工时
    :param personal: 人员
    :param st_date: 出勤起始日期
    :param ed_date: 出勤截止日期
    :return: 统计工时
    """
    """统计上午出勤工时"""
    _sql = u'select count(*) from checkon_t where KQ_NAME="%s" and created_at>="%s" and created_at<"%s" and' %\
           (personal, st_date, ed_date)
    _sql += u' (KQ_AM_STATE="正常" OR KQ_AM_STATE like "迟到%" OR KQ_AM_STATE="出差")'

    _count = mysql_db.count(_sql)
    _total = _count * 4

    """统计下午出勤工时"""
    _sql = u'select count(*) from checkon_t where KQ_NAME="%s" and created_at>="%s" and created_at<"%s" and' % \
           (personal, st_date, ed_date)
    _sql += u' (KQ_PM_STATE="正常" OR KQ_PM_STATE like "迟到%" OR KQ_PM_STATE="出差")'

    _count = mysql_db.count(_sql)
    _total += _count * 4

    return _total

