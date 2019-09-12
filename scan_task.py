# -*- coding: utf-8 -*-
#
#   扫描工作日志，获取人员工作量-日期分布
#   =====================================
#   2019.8.1 @Chengdu
#

import matplotlib.pyplot as plt
from datetime import datetime

from DataHandler import date
import mongodb_class

mongo_db = mongodb_class.mongoDB()
date_obj = date.DateObject()

members = [
    u"刘牧晨",
    u"张家龙",
    u"王鑫",
    u"张少琳",
    u"王媛媛",
    u"崔富",
    u"薛炳乾",
    u"刘俊磊",
    u"张桢",
    u"刘宁",
    u"李玉雷",
    u"王旭",
    u"张秀",
    u"余天翔",
    u"王云麒",
    u"刘彩彩",
    u"韩亚楠",
    u"陈晨",
    u"余林洪",
    u"李忠泽",
    u"秦仕林",
    u"侯丹枫",
]

member_stat = {}
member_rec = {}
member_stat_en = False


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


def member_hdr(member, _date, summary):
    global member_rec, member_stat, members

    if member in members:
        member_stat[member] += 1
        if member not in member_rec:
            member_rec[member] = []
        member_rec[member].append((_date, summary))


def func_worklog():
    global mongo_db, date_obj, member_stat_en, members

    mongo_db.connect_db('WORK_LOGS')
    _rec = do_search('worklog', {})
    for _r in _rec:
        _date = date.get_date(_r['started'])
        date_obj.add(_date, _r['author'])
        if member_stat_en:
            member_hdr(_r['author'], _date, _r['comment'])


def func_pmdaily():
    global mongo_db, date_obj, member_stat_en, members

    mongo_db.connect_db('PM_DAILY')
    _rec = do_search('today_task', {})
    for _r in _rec:
        _date = date.get_date(_r['daily_date'])
        date_obj.add(_date, _r['member'])
        if member_stat_en:
            member_hdr(_r['member'], _date, _r['summary'])


def func_star_task():
    global mongo_db, date_obj, member_stat_en, members

    mongo_db.connect_db('ext_system')
    _rec = do_search('star_task', {})
    for _r in _rec:
        if u"开始时间" in _r:
            _date = date.get_date(_r[u'开始时间'])
            date_obj.add(_date, _r[u'责任人'])
            if member_stat_en:
                member_hdr(_r[u'责任人'], _date, _r[u'任务描述'])


def func_devops_task():
    global mongo_db, date_obj, member_stat_en, members

    mongo_db.connect_db('ext_system')
    _rec = do_search('devops_task', {})
    for _r in _rec:
        _member = _r[u'执行者'].split("(")[0]
        _date = date.get_date(_r[u'开始时间'])
        date_obj.add(_date, _member)
        if member_stat_en:
            member_hdr(_member, _date, _r[u'标题'])


def func_ops_task():
    global mongo_db, date_obj, member_stat_en, members

    mongo_db.connect_db('ext_system')
    _rec = do_search('ops_task', {})
    for _r in _rec:
        if u"日期" in _r:
            _date = date.get_date(_r[u'日期'])
            date_obj.add(_date, _r[u'执行人'])
            if member_stat_en:
                member_hdr(_r[u'执行人'], _date, _r[u'任务'])


def func_ops_task_bj():
    global mongo_db, date_obj, member_stat_en, members

    mongo_db.connect_db('ext_system')
    _rec = do_search('ops_task_bj', {})
    for _r in _rec:
        if u"创建于" in _r:
            _date = date.get_date(_r[u'创建于'])
            if u"技术-处理人" in _r:
                if member_stat_en:
                    member_hdr(_r[u'技术-处理人'], _date, _r[u'主题'])
                date_obj.add(_date, _r[u'技术-处理人'])
            else:
                if member_stat_en:
                    member_hdr(_r[u'故障处理人'], _date, _r[u'主题'])
                date_obj.add(_date, _r[u'故障处理人'])


def func_tower():
    global mongo_db, date_obj, member_stat_en, members

    mongo_db.connect_db('ext_system')
    _rec = do_search('tower', {})
    for _r in _rec:
        if u"完成时间" in _r:
            _date = date.get_date(_r[u'完成时间'])
            date_obj.add(_date, _r[u'负责人'])
            if member_stat_en:
                member_hdr(_r[u'负责人'], _date, _r[u'任务描述'])


def show_plot(x, y, _max, w, c):
    plt.rcdefaults()
    plt.figure(dpi=128, figsize=(10, 4))
    plt.bar(x, y, width=w, color=c, alpha=0.8, linewidth=0)
    plt.plot([x[0], x[-1]], [_max, _max], 'r--', linewidth=0.5)
    plt.gcf().autofmt_xdate()
    plt.xlabel("Date")
    plt.ylabel("Number of staff")
    plt.tick_params(axis='both', which='major', labelsize=8)
    plt.xlim(x[0], x[-1])
    plt.show()


def main():
    """
    主程序
    :return:
    """
    global date_obj, member_stat, members, member_stat_en

    member_stat_en = True
    for _m in members:
        member_stat[_m] = 0

    years = []
    vals = []
    recs = []
    max = {"date": "", "val": 0}
    year_month = {}

    func_worklog()
    func_pmdaily()
    func_star_task()
    func_devops_task()
    func_ops_task()
    func_ops_task_bj()
    func_tower()

    for _m in member_stat:
        print(u"> %s: %d" % (_m, member_stat[_m]))
        if _m in member_rec:
            for _r in member_rec[_m]:
                print "\t\t", _r[0], ":", _r[1]
            print("><")

    _stat = date_obj.stat()
    for _date in sorted(_stat):
        if _date > "20180100":
            if max['val'] < len(_stat[_date]):
                max['val'] = len(_stat[_date])
                max['date'] = _date

            _ym = _date[:6]
            if _ym not in year_month:
                year_month[_ym] = []
            year_month[_ym].append(len(_stat[_date]))

            print _date, ":",
            print "=" * len(_stat[_date]), " [%d]" % len(_stat[_date])
            # print("\t> %s: %d" % (_date, len(_stat[_date])))

            if len(_date) == 8:
                years.append(datetime.strptime(_date, "%Y%m%d"))
                vals.append(len(_stat[_date]))
                _c = 0
                for _i in _stat[_date]:
                    _c += _stat[_date][_i]
                recs.append(_c)

    show_plot(years, vals, max['val'], 2, 'blue')
    show_plot(years, recs, max['val'], 2, 'blue')

    years = []
    vals = []
    print("\nMax @ %s: %d" % (max['date'], max['val']))
    print("Sum: %d" % date_obj.get_sum())

    for _n in _stat[max['date']]:
        print _n, u"、",

    for _v in sorted(year_month):
        print _v, ": ", sorted(year_month[_v], reverse=True)[0]
        _vv = _v + "01"
        years.append(datetime.strptime(_vv, "%Y%m%d"))
        vals.append(sorted(year_month[_v], reverse=True)[0])

    show_plot(years, vals, max['val'], 10, 'blue')


if __name__ == '__main__':
    main()

