#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
#
#   研发管理MIS系统：行为分析
#   =========================
#   2019.2.13 @Chengdu
#
#

from __future__ import unicode_literals

import handler

try:
    import configparser as configparser
except Exception:
    import ConfigParser as configparser

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

"""全员"""
Personals = {}

"""关键词
import os

conf = configparser.ConfigParser()
conf.read(os.path.split(os.path.realpath(__file__))[0] + '/keyword.cnf', encoding="utf-8-sig")

key_object = conf.get('key', 'object')
key_active = conf.get('key', 'active')
key_depth = conf.get('key', 'depth')
"""

object_class = {
    u"云产品": [
        u"FAST",
        u"MIR",
        u"PULSAR",
        u"WH",
        u"WHITE",
        u"APOLLO",
    ],
    u"大数据产品": [
        u"HUBBLE",
    ],
    u"OneX": [
        u"ONE",
    ],
    u"会议": [
        u"会议",
        u"例会",
    ],
    u"界面": [
        u"门户",
        u"界面",
        u"风格",
        u"大屏",
    ],
    u"需求": [
        u"客户",
        u"需求",
    ],
    u"设计&开发": [
        u"方案",
        u"预案",
        u"效果图",
        u"模型",
        u"模块",
        u"流程",
        u"程序",
        u"代码",
        u"接口",
        u"API",
    ],
    u"缺陷&问题": [
        u"BUG",
        u"缺陷",
        u"问题",
    ],
    u"数据": [
        u"数据",
    ],
    u"服务&容器": [
        u"服务",
        u"容器",
    ],
    u"任务": [
        u"任务",
    ],
    u"产品": [
        u"产品",
    ],
    u"项目": [
        u"项目",
    ],
}

key_object = [u"产品",
              u"项目",
              u"FAST",
              u"HUBBLE",
              u"MIR",
              u"PULSAR",
              u"WH",
              u"WHITE",
              u"ONE",
              u"APOLLO",
              u"BUG",
              u"模型",
              u"模块",
              u"流程",
              u"程序",
              u"缺陷",
              u"问题",
              u"服务",
              u"容器",
              u"任务",
              u"接口",
              u"代码",
              u"需求",
              u"例会",
              u"会议",
              u"门户",
              u"界面",
              u"风格",
              u"大屏",
              u"客户",
              u"方案",
              u"预案",
              u"数据",
              u"效果图",
              u"API"]

active_class = {
    u"增删改查": [
        u"增",
        u"减",
        u"改",
        u"删",
        u"写",
    ],
    u"参与": [
        u"参加",
        u"讨论",
        u"评审",
        u"了解",
        u"获取",
],
    u"改进": [
        u"梳理",
        u"整理",
        u"处理",
        u"调整",
        u"解决",
        u"优化",
    ],
    u"调测": [
        u"联调",
        u"测试",
        u"验证",
        u"排查",
        u"定位",
    ],
    u"管理": [
        u"安排",
        u"分配",
    ],
    u"设计": [
        u"设计",
        u"迭代",
        u"变更",
    ],
    u"执行": [
        u"制作",
        u"支撑",
        u"支持",
        u"部署",
        u"提交",
        u"迁移",
    ]
}

key_active = [u"参加",
              u"增",
              u"减",
              u"改",
              u"删",
              u"制作",
              u"修",
              u"处理",
              u"调整",
              u"联调",
              u"解决",
              u"测试",
              u"写",
              u"验证",
              u"排查",
              u"定位",
              u"优化",
              u"了解",
              u"梳理",
              u"整理",
              u"安排",
              u"分配",
              u"部署",
              u"提交",
              u"评审",
              u"设计",
              u"支撑",
              u"支持",
              u"变更",
              u"迭代",
              u"迁移",
              u"讨论",
              u"获取"]
key_depth = [u"已",
             u"完成",
             u"结束",
             u"交付",
             u"正在",
             u"过程中"]


def count(src, word):

    _count = 0
    _idx = 0
    _len = len(word)
    _src = src
    while True:
        _idx = _src.find(word)
        if _idx < 0:
            break
        _count += 1
        _idx += _len
        _src = _src[_idx:]

    return _count


def main():
    global Personals, key_object, key_active, key_depth

    _issues = []
    for _job in handler.pd_list:
        handler.mongo_db.connect_db(_job)
        _cur = handler.mongo_db.handler("worklog", "find")
        for _v in _cur:
            if _v.has_key('author'):
                if _v['author'] not in Personals:
                    Personals[_v['author']] = {'comment': '', 'object': {}, 'active': {}, 'depth': {},
                                               'subject_pd': {}, 'subject_pj': {}, 'issues': [], 'issue': 0}
                Personals[_v['author']]['comment'] += _v['comment'].\
                    replace('"', '').\
                    replace("'", '').\
                    replace(' ', '').\
                    replace('\n', '').\
                    replace('\r', '').upper()

                Personals[_v['author']]['issues'].append(_v['issue'])

                if _job not in Personals[_v['author']]['subject_pd']:
                    Personals[_v['author']]['subject_pd'][_job] = 0
                Personals[_v['author']]['subject_pd'][_job] += 1
                Personals[_v['author']]['issue'] += 1

        for _i in Personals[_v['author']]['issues']:
            _cur = handler.mongo_db.handler("issue", "find_one", {"issue": _i})
            if _cur is not None:
                Personals[_v['author']]['comment'] += _cur['summary']

    for _job in handler.pj_list:
        handler.mongo_db.connect_db(_job)
        _cur = handler.mongo_db.handler("worklog", "find")
        for _v in _cur:
            if _v.has_key('author'):
                if _v['author'] not in Personals:
                    Personals[_v['author']] = {'comment': '', 'object': {}, 'active': {}, 'depth': {},
                                               'subject_pd': {}, 'subject_pj': {}, 'issues': [], 'issue': 0}
                Personals[_v['author']]['comment'] += _v['comment'].\
                    replace('"', '').\
                    replace("'", '').\
                    replace(' ', '').\
                    replace('\n', '').\
                    replace('\r', '').upper()

                if _job not in Personals[_v['author']]['subject_pj']:
                    Personals[_v['author']]['subject_pj'][_job] = 0
                Personals[_v['author']]['subject_pj'][_job] += 1
                Personals[_v['author']]['issue'] += 1

    for _p in Personals:
        for _obj in sorted(key_object):
            if _obj not in Personals[_p]['object']:
                Personals[_p]['object'][_obj] = 0
            Personals[_p]['object'][_obj] += count(Personals[_p]['comment'], _obj)
        for _act in sorted(key_active):
            if _act not in Personals[_p]['active']:
                Personals[_p]['active'][_act] = 0
            Personals[_p]['active'][_act] += count(Personals[_p]['comment'], _act)
        for _dep in sorted(key_depth):
            if _dep not in Personals[_p]['depth']:
                Personals[_p]['depth'][_dep] = 0
            Personals[_p]['depth'][_dep] += count(Personals[_p]['comment'], _dep)

        _issue_sum = 0
        print _p, Personals[_p]['issue']
        print("\n>>> Subject[PD] <<<")
        for _obj in Personals[_p]['subject_pd']:
            print _obj, Personals[_p]['subject_pd'][_obj], ";",
            _issue_sum += Personals[_p]['subject_pd'][_obj]
        print("\n>>> Subject[PJ] <<<")
        for _obj in Personals[_p]['subject_pj']:
            print _obj, Personals[_p]['subject_pj'][_obj], ";",
            _issue_sum += Personals[_p]['subject_pj'][_obj]

        _sum = {}
        print("\n>>> Object <<<")
        for _obj in sorted(object_class):
            if _obj not in _sum:
                _sum[_obj] = 0
            for _o in object_class[_obj]:
                _sum[_obj] += Personals[_p]['object'][_o]

            print _obj, float(_sum[_obj])/float(_issue_sum), ";",

        print("\n>>> Active <<<")
        for _obj in sorted(active_class):
            if _obj not in _sum:
                _sum[_obj] = 0
            for _o in active_class[_obj]:
                _sum[_obj] += Personals[_p]['active'][_o]

            print _obj, float(_sum[_obj])/float(_issue_sum), ";",

        print("\n>>> Depth <<<")
        for _obj in Personals[_p]['depth']:
            print _obj, Personals[_p]['depth'][_obj], ";",
        print("\n"+"-"*16)


if __name__ == '__main__':
    main()
