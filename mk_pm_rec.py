# -*- coding: utf-8 -*-
#
#   生成数据文件，并通过邮件发送
#   ============================
#   2019.8.1 @Chengdu
#

from DataHandler import exceltools
import mongodb_class
mongo_db = mongodb_class.mongoDB()

line_number = 1


def write_title(_book, _titles):
    _v = 0
    for _t in _titles:
        _book.write((0, _v, _t))
        _v += 1


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


def func_jira(_book):
    """
    写jira明细
    :param _book: 文档
    :return:
    """
    global mongo_db, line_number

    mongo_db.connect_db('WORK_LOGS')
    _rec = do_search('worklog', {'issue': {'$regex': "JDWL-"}})
    _l = line_number
    for _r in _rec:
        _book.write((_l, 0, _r['started'].split('T')[0]))
        _book.write((_l, 1, _r['author']))
        _book.write((_l, 2, _r['comment']))
        _book.write((_l, 3, _r['timeSpent']))
        _l += 1
    line_number = _l


def func_star_task(_book):
    """
    写jira明细
    :param _book: 文档
    :return:
    """
    global mongo_db, line_number

    mongo_db.connect_db('ext_system')
    _rec = do_search('star_task', {u'分类': u"嘉定SBU项目"})
    _l = line_number
    for _r in _rec:
        _book.write((_l, 0, _r[u'完成时间'].split(' ')[0]))
        _book.write((_l, 1, _r[u'责任人']))
        _book.write((_l, 2, _r[u'任务描述']))
        _book.write((_l, 3, u"当天"))
        _l += 1


def func_member_jira(_members, _book):
    """
    写jira明细
    :param _members: 人员列表
    :param _book: 文档
    :return:
    """
    global mongo_db, line_number

    _l = line_number

    mongo_db.connect_db('WORK_LOGS')
    for _member in _members:
        _rec = do_search('worklog', {'author': _member})
        for _r in _rec:
            if u"嘉定" in _r["project"] or u"嘉定" in _r["comment"]:
                _book.write((_l, 0, _r['started'].split('T')[0]))
                _book.write((_l, 1, _r['author']))
                _book.write((_l, 2, _r['comment']))
                _book.write((_l, 3, _r['timeSpent']))
                _book.write((_l, 4, _r['project']))
                _l += 1
    line_number = _l


def func_member_star_task(_members, _book):
    """
    写jira明细
    :param _members：人员列表
    :param _book: 文档
    :return:
    """
    global mongo_db, line_number

    mongo_db.connect_db('ext_system')
    _l = line_number
    for _member in _members:
        _rec = do_search('star_task', {u'责任人': _member})
        for _r in _rec:
            if u"嘉定" in _r[u'任务描述'] or "SBU" in _r[u'任务描述']:
                _book.write((_l, 0, _r[u'完成时间'].split(' ')[0]))
                _book.write((_l, 1, _r[u'责任人']))
                _book.write((_l, 2, _r[u'任务描述']))
                _book.write((_l, 3, u"当天"))
                _book.write((_l, 4, u"项目要求"))
                _l += 1


def main():
    """
    主程序
    :return:
    """
    global line_number

    """创建excel文件"""
    book = exceltools.ExcelTools()
    book.open("pj_work_daily")
    book.add_sheet(u"工作日志")
    write_title(book, [u"日期", u"人员", u"内容", u"工时"])
    func_jira(book)
    func_star_task(book)
    members = [u"查明", u"孙莎莎", u"王奕骅", u"梁雨", u"武静"]
    book.add_sheet(u"人员日志")
    line_number = 1
    write_title(book, [u"日期", u"人员", u"内容", u"工时", u"项目"])
    func_member_jira(members, book)
    func_member_star_task(members, book)
    book.close()


if __name__ == '__main__':
    main()

