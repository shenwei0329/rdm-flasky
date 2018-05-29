#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
#

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from pylab import plot, show, savefig, xlim, figure, \
                hold, ylim, legend, boxplot, setp, axes
import time,random
import MySQLdb, math
import mysql_hdr
import datetime
import sys
import pandas as pd
from numpy import mean, median, std
from matplotlib.dates import AutoDateLocator, DateFormatter
from matplotlib import transforms

from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']

reload(sys)
sys.setdefaultencoding('utf-8')

"""
设置图例显示的位置
label_pos:
===========

'best'         : 0, (only implemented for axes legends)(自适应方式)
'upper right'  : 1,
'upper left'   : 2,
'lower left'   : 3,
'lower right'  : 4,
'right'        : 5,
'center left'  : 6,
'center right' : 7,
'lower center' : 8,
'upper center' : 9,
'center'       : 10,
"""
__test = False


def doBox(label,datas,y_line=None,y_limit=None,y_label=None,x_label=None):
    fig = figure()
    ax = axes()
    hold(True)

    _bx = []
    for _data in datas:
        _x = boxplot(_data, positions=range(1, len(label)+1), widths=0.6)
        _bx.append(_x)

    # set axes limits and labels
    xlim(0, len(label)+1)
    if y_limit is not None:
        ylim(y_limit[0], y_limit[1])
    if y_line is not None:
        for _l in y_line:
            plt.axhline(y=_l,linestyle='-', linewidth=1, color='red')
    ax.set_xticklabels(label)
    if y_label is not None:
        plt.ylabel(y_label)
    if x_label is not None:
        plt.xlabel(x_label)

    _fn = 'pic/%s-box.png' % time.time()
    if not __test:
        savefig(_fn, dpi=120)
    else:
        show()
    return _fn, _bx


def doBar(title, y_label, x_label, datas, label=None, y_limit=None):

    plt.figure()
    ind = np.arange(len(x_label))  # the x locations for the groups
    _b = np.zeros(len(x_label))     # the x locations for the groups
    _i = 0
    for _d in datas:
        if label is not None:
            plt.bar(ind, _d[0], 0.35, color=_d[1], bottom=_b, label=label[_i])
        else:
            plt.bar(ind, _d[0], 0.35, bottom=_b, color=_d[1])
        _b = _b + _d[0]
        print _b
        _i += 1
    if y_limit is not None:
        ylim(0,y_limit)
    plt.ylabel(y_label)
    plt.title(title)
    plt.xticks(ind, x_label)
    if label is not None:
        plt.legend()
    _fn = 'pic/%s-bar.png' % time.time()
    if not __test:
        savefig(_fn, dpi=120)
    else:
        show()
    return _fn


def doDotBase(title, y_label, x_label, datas, limit=None, label_pos=None, lines=None, ylines=None, dots=None):

    rcParams.update({
    'font.family':'sans-serif',
    'font.sans-serif':[u'SimHei'],
    'axes.unicode_minus':False,
    'font.size':8,
    })

    _show_date = False

    if _show_date:
        autodates = AutoDateLocator()
        yearsFmt = DateFormatter('%Y-%m-%d %H:%M:%S')
        fig = plt.figure(figsize=[10, 12], dpi=120)
        fig.autofmt_xdate()
        plt.xticks(rotation=45)
        ax = fig.add_subplot(111)
        ax_twiny = ax.twiny()
        ax_twiny.grid(False)
        ax_twiny.set_xticks([])
        ax.xaxis.set_major_locator(autodates)       # 设置时间间隔  
        ax.xaxis.set_major_formatter(yearsFmt)      # 设置时间显示格式  
        ax.set_xticks(pd.date_range(start='2017-9-27 00:00:00', end='2018-03-31 23:59:59', freq='3D'))
        """设定显示的时间段"""
        _day = datetime.date.today().day
        _month = datetime.date.today().month
        if _day < 27:
            _day += 3
        else:
            _month += 1
            _day = 1
        _end_date = datetime.date.today().replace(day=_day, month=_month)
        ax.set_xlim("2017-9-1 00:00:00", "%s 00:00:00" % _end_date)
    else:
        plt.figure()

    for _data in datas:
        _color = _data[1]
        _dot = _data[2]
        _label = _data[3]
        plt.plot(range(len(_data[0])), _data[0], _dot, label=_label, color=_color)

    if limit is not None:
        ylim(limit[0],limit[1])

    if dots is not None:
        for _dot in dots:
            plt.scatter(_dot[0], _dot[1], marker=_dot[2], color=_dot[3], label=_dot[4], alpha=0.5)

    if lines is not None:
        for _line in lines:
            plt.axvline(x=_line[0], linestyle=_line[1], linewidth=2, color=_line[2], label=_line[3])

    if ylines is not None:
        for _line in ylines:
            plt.axhline(y=_line[0], linestyle=_line[1], linewidth=1, color=_line[2], label=_line[3])

    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.title(title)
    if label_pos is None:
        plt.legend()
    else:
        plt.legend(loc=label_pos)

    _fn = 'pic/%s-bar.png' % time.time()
    if not __test:
        plt.savefig(_fn, dpi=120)
    else:
        plt.show()
    return _fn


def doStem(title, y_label, x_label, datas, limit=None, label_pos=None, lines=None, ylines=None, dots=None):

    plt.figure()
    for _data in datas:
        _color = _data[1]
        _dot = _data[2]
        _label = _data[3]
        markerline, stemlines, baseline = plt.stem(_data[0][0],_data[0][1],_dot, label=_label)
        plt.setp(markerline, 'markerfacecolor', _color)
        plt.setp(stemlines, 'color', _color, 'linewidth', 1)
        plt.setp(baseline, 'color', 'k', 'linewidth', 1)

    if limit is not None:
        ylim(limit[0],limit[1])

    if dots is not None:
        for _dot in dots:
            plt.scatter(_dot[0], _dot[1], marker=_dot[2], color=_dot[3], label=_dot[4])

    if lines is not None:
        for _line in lines:
            plt.axvline(x=_line[0], linestyle=_line[1], linewidth=1, color=_line[2], label=_line[3])

    if ylines is not None:
        for _line in ylines:
            plt.axhline(y=_line[0], linestyle=_line[1], linewidth=1, color=_line[2], label=_line[3])

    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.title(title)
    if label_pos is None:
        plt.legend()
    else:
        plt.legend(loc=label_pos)

    _fn = 'pic/%s-stem.png' % time.time()
    if not __test:
        plt.savefig(_fn, dpi=120)
    else:
        plt.show()
    return _fn


def doLine(title, y_label, x_label, datas, limit=None, label_pos=None, lines=None, ylines=None, dots=None):

    plt.figure()
    _max = 0
    for _data in datas:
        _color = _data[1]
        _dot = _data[2]
        _label = _data[3]
        for _i in _data[0][0]:
            if _max < _data[0][1][_i][1]+1:
                _max = _data[0][1][_i][1]+1
            plt.plot([_i, _i], [_data[0][1][_i][0], _data[0][1][_i][1]], _dot, linewidth=3, color=_color)
        plt.plot([_i, _i], [_data[0][1][_i][0], _data[0][1][_i][1]], _dot, linewidth=3, color=_color, label=_label)

    ylim(-1, _max+float(_max)*0.1)

    if dots is not None:
        for _dot in dots:
            plt.scatter(_dot[0], _dot[1], marker=_dot[2], color=_dot[3], label=_dot[4])

    if lines is not None:
        for _line in lines:
            plt.axvline(x=_line[0], linestyle=_line[1], linewidth=1, color=_line[2], label=_line[3])

    if ylines is not None:
        for _line in ylines:
            plt.axhline(y=_line[0], linestyle=_line[1], linewidth=1, color=_line[2], label=_line[3])

    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.title(title)
    if label_pos is None:
        plt.legend()
    else:
        plt.legend(loc=label_pos)

    _fn = 'pic/%s-line.png' % time.time()
    if not __test:
        plt.savefig(_fn, dpi=120)
    else:
        plt.show()
    return _fn


def doBarH(title, y_label, x_label, datas):

    plt.figure()
    ind = np.arange(len(x_label))+1  # the x locations for the groups
    plt.barh(ind, datas, 0.35, 0.5, align='edge', color='#afafaf')
    plt.xlabel(y_label)
    plt.title(title)
    plt.yticks(ind, x_label)
    _fn = 'pic/%s-bar.png' % time.time()
    if not __test:
        savefig(_fn, dpi=120)
    else:
        show()
    return _fn


def BurnDownChart(dots):
    """
    制作“燃尽”图
    :param dots: [['日期'，Y-值，类型],...]
    :return: 图文件存放路径
    """

    global __test

    """作图"""
    rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': [u'SimHei'],
        'axes.unicode_minus': False,
        'font.size': 6,
    })

    autodates = AutoDateLocator()
    yearsFmt = DateFormatter('%Y-%m-%d')
    fig = figure(figsize=[10, 6], dpi=120)

    ax = fig.add_subplot(111)
    fig.autofmt_xdate()                         # 设置x轴时间外观
    ax.xaxis.set_major_locator(autodates)       # 设置时间间隔
    ax.xaxis.set_major_formatter(yearsFmt)      # 设置时间显示格式

    """设定显示的时间段"""
    _end_date = datetime.date.today() + datetime.timedelta(days=10)
    ax.set_xticks(pd.date_range(start='2017-12-10', end='%s' % _end_date, freq='3D'))
    # ax.set_xlim("2017-12-10", "%s" % _end_date)
    # ax.set_ylim(0, total+1)

    _leg = []
    for __i in range(5):
        _leg.append(None)

    for __dot in dots:
        _done_lines_dots = {'date':[], 'dot':[]}
        _testing_lines_dots = {'date':[], 'dot':[]}
        _wait_testing_lines_dots = {'date':[], 'dot':[]}
        _doing_lines_dots = {'date':[], 'dot':[]}
        _waiting_lines_dots = {'date':[], 'dot':[]}
        for _dot in __dot['dots']:
            if _dot[2] == 'done':
                _done_lines_dots['date'].append(_dot[0])
                _done_lines_dots['dot'].append(_dot[1])
            elif _dot[2] == 'doing':
                _doing_lines_dots['date'].append(_dot[0])
                _doing_lines_dots['dot'].append(_dot[1])
            elif _dot[2] == 'waiting':
                _waiting_lines_dots['date'].append(_dot[0])
                _waiting_lines_dots['dot'].append(_dot[1])
            elif _dot[2] == 'wait_testing':
                _wait_testing_lines_dots['date'].append(_dot[0])
                _wait_testing_lines_dots['dot'].append(_dot[1])
            else:
                _testing_lines_dots['date'].append(_dot[0])
                _testing_lines_dots['dot'].append(_dot[1])
            # _leg[0] = ax.scatter(_dot[0], _dot[1], color=_issue_point_color[_dot[2]], marker=_issue_point_marker[_dot[2]])

        _leg[0] = ax.fill_between(_done_lines_dots['date'],
                                  __dot['count'],
                                  _done_lines_dots['dot'],
                                  facecolor='lightcyan')
        _leg[1] = ax.fill_between(_done_lines_dots['date'],
                        _done_lines_dots['dot'],
                        _testing_lines_dots['dot'],
                        facecolor='lightpink')
        _leg[2] = ax.fill_between(_done_lines_dots['date'],
                        _testing_lines_dots['dot'],
                        _wait_testing_lines_dots['dot'],
                        facecolor='lightgoldenrodyellow')
        _leg[3] = ax.fill_between(_done_lines_dots['date'],
                        _wait_testing_lines_dots['dot'],
                        _doing_lines_dots['dot'],
                        facecolor='lightgreen')
        _leg[4] = ax.fill_between(_done_lines_dots['date'],
                        _doing_lines_dots['dot'],
                        0,
                        facecolor='cyan')
        # plt.setp(_lines, color='r')

    ax.set_xlabel(u'日期', fontsize=11)
    ax.set_ylabel(u'任务量', fontsize=11)
    ax.grid(True)
    ax.legend(_leg,
              [u"已完成",
               u"测试中",
               u"等测中",
               u"处理中",
               u"等待中"],
              loc=1,
              fontsize=12)

    """图示各sprint的区域"""
    trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)
    for _p in dots:
        if _p['sprint'][-1] != 'Active':
            _c = 'lightblue'
        else:
            _c = 'lightgreen'
        ax.fill_between(_p['sprint'][:-1], 0, 1, transform=trans, alpha=0.3, color=_c)
        ax.plot(_p['sprint'][:-1], [_p['count'], 0], color='r', linewidth=1, alpha=0.3)

    plt.title(u'任务燃尽图', fontsize=12)
    plt.subplots_adjust(left=0.08, right=0.98, bottom=0.06, top=0.96)

    _fn = 'pic/%s-issue-burndown.png' % time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    if not __test:
        plt.savefig(_fn, dpi=120)
    else:
        plt.show()
    return _fn


def TimeBurnDownChart(dots):
    """
    制作工时“燃尽”图
    :param dots: [['日期'，Y-值],...]
    :return: 图文件存放路径
    """

    global __test

    """作图"""
    rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': [u'SimHei'],
        'axes.unicode_minus': False,
        'font.size': 6,
    })

    autodates = AutoDateLocator()
    yearsFmt = DateFormatter('%Y-%m-%d')
    fig = figure(figsize=[10, 6], dpi=120)

    ax = fig.add_subplot(111)
    fig.autofmt_xdate()                         # 设置x轴时间外观
    ax.xaxis.set_major_locator(autodates)       # 设置时间间隔
    ax.xaxis.set_major_formatter(yearsFmt)      # 设置时间显示格式

    """设定显示的时间段"""
    _end_date = datetime.date.today() + datetime.timedelta(days=10)
    ax.set_xticks(pd.date_range(start='2017-12-10', end='%s' % _end_date, freq='3D'))
    # ax.set_xlim("2017-12-10", "%s" % _end_date)
    # ax.set_ylim(0, total+1)

    _leg = [None, None, None]
    for __dot in dots:
        _spent_lines_dots = {'date':[], 'dot':[]}
        _org_lines_dots = {'date':[], 'dot':[]}
        for _dot in __dot['dots']:
            if _dot[2] == 'spent':
                _spent_lines_dots['date'].append(_dot[0])
                _spent_lines_dots['dot'].append(_dot[1])
            else:
                _org_lines_dots['date'].append(_dot[0])
                _org_lines_dots['dot'].append(_dot[1])

        _leg[0] = ax.fill_between(_spent_lines_dots['date'],
                                  __dot['count'],
                                  _spent_lines_dots['dot'],
                                  facecolor='lightcyan',
                                  alpha=0.6)

        _leg[1] = ax.fill_between(_spent_lines_dots['date'],
                                  _spent_lines_dots['dot'],
                                  0,
                                  facecolor='lightpink',
                                  alpha=0.7)

        _leg[2] = ax.fill_between(_spent_lines_dots['date'],
                                  _org_lines_dots['dot'],
                                  0, # _spent_lines_dots['dot'],
                                  facecolor='lightyellow',
                                  alpha=0.3)
        # plt.setp(_lines, color='r')

    ax.set_xlabel(u'日期', fontsize=11)
    ax.set_ylabel(u'工时', fontsize=11)
    ax.grid(True)
    ax.legend(_leg,
              [u"规划", u"执行", u"估计"],
              loc=1,
              fontsize=12)

    """图示各sprint的区域"""
    trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)
    for _p in dots:
        if _p['sprint'][-1] != 'Active':
            _c = 'lightblue'
        else:
            _c = 'lightgreen'
        ax.fill_between(_p['sprint'][:-1], 0, 1, transform=trans, alpha=0.1, color=_c)
        ax.plot(_p['sprint'][:-1], [0, _p['count']], color='r', linewidth=1, alpha=0.3)

    plt.title(u'工时燃尽图', fontsize=12)
    plt.subplots_adjust(left=0.08, right=0.98, bottom=0.06, top=0.96)

    _fn = 'pic/%s-time-issue-burndown.png' % time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    if not __test:
        plt.savefig(_fn, dpi=120)
    else:
        plt.show()
    return _fn


def doIssueAction(issues, dots, figsize=[10, 12]):
    """
    制作“活动分布”图
    :param issues: 任务
    :param dots: 活动
    :param figsize: 图大小
    :return:
    """

    global __test

    _issue_point_marker = {'timeoriginalestimate': 'v',
                           'timeestimate': 'o',
                           'timespent': '^',
                           'WorklogTimeSpent': 's',
                           'status': '+',
                           u"bug产生人": '*',
                          'resolution': '>'}

    _issue_point_color = {'timeoriginalestimate': 0,
                          'timeestimate': 1,
                          'timespent': 2,
                          'WorklogTimeSpent': 3,
                          'status': 4,
                          u"bug产生人": 5,
                          'resolution': 6}

    """
    _issue_point_marker = {"agg_time": 'v',
                           "org_time": 'o',
                           "spent_time": '^',
                           "status": 's',
                           "updated": '+',
                           "landmark": '>',
                           "sprint": '<',
                           "users": 'x',
                           "epic_link": 'D',
                           "lastViewed": 'p',
                           }

    _issue_point_color = {"agg_time": 1,
                           "org_time": 2,
                           "spent_time": 3,
                           "status": 4,
                           "updated": 5,
                           "landmark": 6,
                           "sprint": 7,
                           "users": 8,
                           "epic_link": 9,
                           "lastViewed": 10,
                           }
    """

    # _colors = plt.cm.BuPu(np.linspace(1, 255, len(_issue_point_marker)+1)); hsv; jet
    _colors = plt.cm.hsv(np.linspace(0.5, 1., len(_issue_point_marker)))
    """作图"""
    rcParams.update({'font.family': 'sans-serif',
                     'font.sans-serif': [u'SimHei'],
                     'axes.unicode_minus': False,
                     'font.size': 6,
                     })

    autodates = AutoDateLocator()
    yearsFmt = DateFormatter('%Y-%m-%d')
    fig = figure(figsize=figsize, dpi=120)

    ax = fig.add_subplot(111)
    fig.autofmt_xdate()                         # 设置x轴时间外观
    ax.xaxis.set_major_locator(autodates)       # 设置时间间隔
    ax.xaxis.set_major_formatter(yearsFmt)      # 设置时间显示格式

    """设定显示的时间段"""
    _day = datetime.date.today().day
    _month = datetime.date.today().month
    if _day < 27:
        _day += 3
    else:
        _month += 1
        _day = 1
    _end_date = datetime.date.today().replace(day=_day, month=_month)

    ax.set_xticks(pd.date_range(start='2018-02-01', end='%s' % _end_date, freq='3D'))
    ax.set_xlim("2018-02-01", "%s" % _end_date)
    ax.set_yticks(range(1, len(issues)+1))
    ax.set_yticklabels(issues,)
    ax.set_ylim(0, len(issues)+1)

    _leg = []
    for __i in range(len(_issue_point_marker)+1):
        _leg.append(None)

    for _dot in dots:
        if _dot[2] in _issue_point_marker:
            _marker = _issue_point_marker[_dot[2]]
            _index = _issue_point_color[_dot[2]]
            _c = _colors[_index]
            # _c = 'k'
            _leg[_index] = ax.scatter(_dot[0], _dot[1], color=_c, marker=_marker, s=30, alpha=0.7)

    ax.set_xlabel(u'日期', fontsize=11)
    ax.set_ylabel(u'任务', fontsize=11)
    ax.grid(True)

    ax.legend(_leg,
              [u"预估工时",
               u"设置工时",
               u"花费工时",
               u"记工时日志",
               u"状态修改",
               u"bug报告",
               u"解决问题"],
              loc=2,
              fontsize=12)

    plt.title(u'任务活动分布图', fontsize=12)
    plt.subplots_adjust(left=0.10, right=0.98, bottom=0.06, top=0.96)

    dt = datetime.datetime.now()
    _fn = 'pic/%s-issue-action.png' % dt.strftime('%Y%m%d%H%M%S%f')
    if not __test:
        plt.savefig(_fn, dpi=120)
    else:
        plt.show()
    return _fn


def doIssueStatus(title, xlabel, issues, dots, dots_s):
    """
    制作“任务状态”图
    :param issues: 状态
    :param dots: 任务
    :param dots_s: 点状态，反应状态变更大小
    :return:
    """

    global __test

    """作图"""
    rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': [u'SimHei'],
    'axes.unicode_minus': False,
    'font.size': 6,
    })

    _colors = plt.cm.nipy_spectral(np.linspace(0.5, 1., 5))

    fig = plt.figure(figsize=[14, 6], dpi=120)
    ax = fig.add_subplot(111)
    plt.xticks(rotation=45)

    ax.set_xlim(0, len(issues)+1)
    ax.set_yticks(range(6))
    ax.set_xticks(range(len(issues)+2))
    ax.set_ylim(0, 6)
    _count = [0, 0, 0, 0, 0]
    _p_dot = None
    _np_dot = None
    _idx = 0

    for _dot in dots:
        __idx = dots_s[issues[_idx]]
        if __idx > 4:
            __idx = 4
        _s = (__idx*2+1) * 20
        if _dot[2] == 'v':
            # _np_dot = ax.scatter(_dot[0], _dot[1], marker=_dot[2], c=_dot[3], s=_s)
            _np_dot = ax.scatter(_dot[0], _dot[1], c=_colors[__idx], s=_s, alpha=0.7)
        else:
            # _p_dot = ax.scatter(_dot[0], _dot[1], marker=_dot[2], c=_dot[3], s=_s)
            _p_dot = ax.scatter(_dot[0], _dot[1], c=_colors[__idx], s=_s, alpha=0.7)
        _count[_dot[1]-1] += 1
        _idx += 1

    ax.set_yticklabels(["",
                        "Wt %03d" % _count[0],
                        "Do %03d" % _count[1],
                        "wT %03d" % _count[2],
                        "Tt %03d" % _count[3],
                        "Cp %03d" % _count[4]], fontsize=12)

    ax.set_ylabel(u"状态：待办Wt，处理中Do，待测试wT，测试中Tt，完成Cp", fontsize=12)
    ax.set_xlabel(xlabel, fontsize=12)
    # ax.legend([_p_dot, _np_dot], [u"计划的", u"非计划的"], fontsize=12)
    plt.title(title, fontsize=14)
    ax.set_xticklabels(issues,)
    ax.grid(True)
    plt.subplots_adjust(left=0.10, right=0.98, bottom=0.12, top=0.96)

    _fn = 'pic/%s-issue-status.png' % time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    if not __test:
        plt.savefig(_fn, dpi=120)
    else:
        plt.show()
    return _fn


def doIssueCost(title, xlabel, issues, dots, max_cost):
    """
    制作“目标预算执行”图
    :param issues: 目标
    :param dots: 预算执行
    :param max_cost: 最大值
    :return:
    """

    global __test

    """作图"""
    rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': [u'SimHei'],
    'axes.unicode_minus': False,
    'font.size': 6,
    })

    fig = plt.figure(figsize=[14, 6], dpi=120)
    ax = fig.add_subplot(111)
    plt.xticks(rotation=45)

    ax.set_xlim(0, len(issues)+1)
    ax.set_xticks(range(len(issues)+2))

    # ax.set_yscale('logit')
    for _dot in dots:
        _v = float(_dot[1])/float(max_cost)
        print _dot[0], _v, _dot[2], _dot[3]
        ax.scatter(_dot[0], _v, marker=_dot[2], c=_dot[3], s=30, alpha=0.5)

    ax.legend([u"计划的预算", u"估计的", u"执行的"], fontsize=12)
    ax.set_ylabel(u"成本", fontsize=12)
    ax.set_xlabel(xlabel, fontsize=12)
    plt.title(title, fontsize=14)
    ax.set_xticklabels(issues,)
    ax.grid(True)
    plt.subplots_adjust(left=0.10, right=0.98, bottom=0.12, top=0.96)

    _fn = 'pic/%s-issue-status.png' % time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    if not __test:
        plt.savefig(_fn, dpi=120)
    else:
        plt.show()
    return _fn


def doSQL(cur,_sql):

    #print(">>>doSQL[%s]" % _sql)
    cur.execute(_sql)
    return cur.fetchall()


def calLvl(lvl, val, max_v):
    """
    获取评价等级
    :param lvl: 评级指标
    :param val: 被评数据
    :param max_v: 最大值
    :return:
    """
    if val <= lvl[0]:
        if lvl[0] > 0:
            return 90. + (val/lvl[0])*10.
        else:
            return 98.
    elif val <= lvl[1]:
        if lvl[1] > lvl[0]:
            return 80. + ((val - lvl[0])/(lvl[1]-lvl[0]))*10.
        else:
            return 88.
    elif val <= lvl[2]:
        if lvl[2] > lvl[1]:
            return 70. + ((val - lvl[1])/(lvl[2]-lvl[1]))*10.
        else:
            return 78.
    elif val <= lvl[3]:
        if lvl[3] > lvl[2]:
            return 60. + ((val - lvl[2])/(lvl[3]-lvl[2]))*10.
        else:
            return 68.
    else:
        if lvl[3] < max_v:
            return 50. + ((val - lvl[3])/(max_v - lvl[3]))*10.
        else:
            return 58.


def getPersonalPlanQ(cur):
    """
    生成个人“任务计划指标”
    :param cur: 数据源
    :return: 指标
    """

    _name = []
    datas = []
    _data = []
    _dd = ()

    """获取员工名称"""
    _sql = 'select MM_XM from member_t'
    _oprs = doSQL(cur, _sql)

    """获取每个人的任务投入指标"""
    _max = 0
    for _opr in _oprs:
        _name.append(u'%s' % _opr[0])
        _sql = 'select TK_GZSJ from task_t where TK_ZXR="%s"' % _opr[0]
        _res = doSQL(cur, _sql)
        _d = ()
        for _v in _res:
            if _v[0] == "#":
                continue
            _d += (int(float(_v[0])),)
            _dd += (int(float(_v[0])),)
        if len(_d) > 0 and _max < max(_d):
            _max = max(_d)
        _data.append(_d)
        datas.append(_data)

    """绘制“总特征”并获取评分参数"""
    _fn1, _bxs = doBox([u'总计'], [[_dd]], y_limit=(-5, _max + 5))

    bx = _bxs[0]
    _lvl = [bx["whiskers"][0].get_ydata()[0],  # 优
            bx["medians"][0].get_ydata()[0],  # 良
            bx["whiskers"][1].get_ydata()[0],  # 中
            bx["whiskers"][1].get_ydata()[1]]  # 差

    _lines = []
    for _l in _lvl:
        _lines.append(_l)

    _fn2, _bxs = doBox(range(len(_name)), datas, y_line=_lines, y_limit=(-5, _max + 5))

    _kv = {}
    _i = 0
    for bx in _bxs:
        _median = bx["medians"][_i].get_ydata()[0]
        if math.isnan(_median):
            _i += 1
            continue
        _kv[_name[_i]] = (_median, calLvl(_lvl, _median, _max))
        _i += 1

    return _fn1, _fn2, _lvl, _kv


if __name__ == '__main__':

    global __test

    __test = True
    _test_case = 3

    db = MySQLdb.connect(host="47.93.192.232", user="root", passwd="sw64419", db="nebula", charset='utf8')
    # db = MySQLdb.connect(host="172.16.101.117", user="root", passwd="123456", db="nebula", charset='utf8')
    cur = db.cursor()
    my_sql = mysql_hdr.SqlService(db)

    if _test_case == 1:
        fn1, fn2, lvl, kv = getPersonalPlanQ(cur)
        for _k in kv:
            print(u'%s: %s => %s' % (_k, kv[_k][0], kv[_k][1]))
    elif _test_case == 2:
        _data = []
        _data.append([[10, 6, 4, 2, 1, 0, 0, 0, 0], "#8f8f8f", "^", u'等待'])
        _data.append([[0,  4, 6, 5, 3, 2, 1, 0, 0], "#f8f8f8", "o", u"执行中"])
        _data.append([[0,  0, 0, 3, 4, 4, 3, 1, 0], "#f8f8f8", "v", u"测试中"])
        _data.append([[0,  0, 0, 0, 2, 3, 6, 9, 10], "#f8f8f8", "*", u"完成"])

        _color = ['g','y','r','k']
        _sql = u'select name from jira_landmark_t where pj_id="FAST"'
        _res = my_sql.do(_sql)
        _ylines = []
        _dots = []
        _i = 0
        _sum = 0
        for _r in _res:
            _sql = u'select count(*) from jira_issue_t where issue_key="landmark" and issue_value="%s"' % _r[0]
            _cnt = my_sql.count(_sql)
            _sum += _cnt
            _ylines.append([_sum, '--', _color[_i], u'%d:%s' % (_cnt,_r[0])])
            _j = 0
            for _st in [u"待办", u"执行中", u"待测试", u"完成"]:
                """
                _sql = u'select count(*) from jira_issue_t where issue_id in ' \
                       u'(select issue_id from jira_issue_t where issue_key="landmark" and ' \
                       u'issue_value="%s") and issue_value="%s"' % (_r[0], _st)
                _cnt = my_sql.count(_sql)
                """
                _cnt = 23
                _dots.append([1, _cnt, ">", _color[_j], None])
                _j += 1
            _i += 1

        doDotBase("Test Case 0002", u"story数", u"时间", _data, label_pos='upper left', ylines=_ylines, dots=_dots)
    elif _test_case == 3:
        _dots = []
        _start_date = pd.date_range(start='2018-02-01', end='2018-03-9', freq='1D')

        for _date in _start_date:
            for _i in range(3):
                _r = random.random() + _i
                if _r > 2:
                    _type = 'done'
                elif _r > 1:
                    _type = 'doing'
                else:
                    _type = 'waiting'
                _dots.append([_date, _r*10, _type])

        BurnDownChart([30, 30], _dots, [['2018-02-03', '2018-02-12', 'b'], ['2018-02-12', '2018-02-28', 'r']])

