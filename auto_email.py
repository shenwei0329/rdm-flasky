# -*- coding: utf-8 -*-
#
#   生成数据文件，并通过邮件发送
#   ============================
#   2019.8.1 @Chengdu
#

from datetime import date
from DataHandler import exceltools
from DataHandler import redis_class


# 研发管理“正文”缓存
key_rdm = redis_class.KeyLiveClass('rdm')
rdm_data = key_rdm.get()
end_month = 12


def func1(_book):
    """
    产品研发资源产品投入
    :param _book: 文档
    :return:
    """
    global rdm_data, end_month
    _l = 1
    for _pd_name in sorted(rdm_data["product_pj_task"]):
        _book.write((_l, 0, _pd_name))
        for _idx in range(1, end_month):
            _book.write((_l, _idx, float(rdm_data["product_pj_task"][_pd_name][_idx])))
        _l += 1
    _book.write((_l, 0, u"合计"))
    for _idx in range(1, end_month):
        _book.write((_l, _idx, float(rdm_data["product_pj_task_sum"][_idx])))


def func2(_book):
    """
    产品研发资源项目投入
    :param _book: 文档
    :return:
    """
    global rdm_data, end_month
    _l = 1
    for _pj_name in sorted(rdm_data["pd_project"]):
        _book.write((_l, 0, _pj_name))
        for _idx in range(1, end_month):
            _book.write((_l, _idx, rdm_data["pd_project"][_pj_name][_idx]/3600.))
        _l += 1
    _book.write((_l, 0, u"合计"))
    for _idx in range(1, end_month):
        _book.write((_l, _idx, float(rdm_data["pd_project_sum"][_idx])))


def func3(_book):
    """
    测试资源投入
    :param _book: 文档
    :return:
    """
    global rdm_data, end_month
    _l = 1
    for _pj_name in sorted(rdm_data["test_task"]):
        _book.write((_l, 0, _pj_name))
        for _idx in range(1, end_month):
            _book.write((_l, _idx, float(rdm_data["test_task"][_pj_name][_idx])))
        _l += 1
    _book.write((_l, 0, u"合计"))
    for _idx in range(1, end_month):
        _book.write((_l, _idx, float(rdm_data["test_task_sum"][_idx])))


def func4(_book):
    """
    研发明细
    :param _book: 文档
    :return:
    """
    global rdm_data, end_month
    _l = 1
    _value = []
    for _v in range(1, end_month):
        _value.append("%02d" % _v)
    for _pj_name in sorted(rdm_data["pd_project"]):
        _book.write((_l, 0, _pj_name))
        _l += 1
        for _t in rdm_data["pd_project"][_pj_name]['member']:
            if _t['date'][5:7] in _value:
                _book.write((_l, 1, _t['date']))
                _book.write((_l, 2, _t['spent_time']/3600.))
                _book.write((_l, 3, _t['summary']))
                _book.write((_l, 4, _t['member']))
                _l += 1


def func5(_book):
    """
    测试明细
    :param _book: 文档
    :return:
    """
    global rdm_data, end_month
    _l = 1
    _value = []
    for _v in range(1, end_month):
        _value.append("%02d" % _v)
    for _pj_name in sorted(rdm_data["test_task"]):
        if _pj_name in ['FAST', 'HUBBLE']:
            continue
        _book.write((_l, 0, _pj_name))
        _l += 1
        for _t in rdm_data["test_task"][_pj_name]['member']:
            if _t['date'][5:7] in _value:
                _book.write((_l, 1, _t['date']))
                _book.write((_l, 2, _t['spent_time']/3600.))
                _book.write((_l, 3, _t['summary']))
                _book.write((_l, 4, _t['member']))
                _l += 1


"""为项目部和财务部提供统计数据"""
For_Pm_Sheet = [
    {
        "page": u"产品研发资源产品投入",
        "title": [u"项目",
                  u"一月",
                  u"二月",
                  u"三月",
                  u"四月",
                  u"五月",
                  u"六月",
                  u"七月",
                  u"八月",
                  u"九月",
                  u"十月",
                  u"十一月",
                  u"十二月",
                  u"合计"
                  ],
        "func": func1
    },
    {
        "page": u"产品研发资源项目投入",
        "title": [u"项目",
                  u"一月",
                  u"二月",
                  u"三月",
                  u"四月",
                  u"五月",
                  u"六月",
                  u"七月",
                  u"八月",
                  u"九月",
                  u"十月",
                  u"十一月",
                  u"十二月",
                  u"合计"
                  ],
        "func": func2},
    {
        "page": u"测试资源投入",
        "title": [u"项目",
                  u"一月",
                  u"二月",
                  u"三月",
                  u"四月",
                  u"五月",
                  u"六月",
                  u"七月",
                  u"八月",
                  u"九月",
                  u"十月",
                  u"十一月",
                  u"十二月",
                  u"合计"
                  ],
        "func": func3},
    {
        "page": u"研发明细",
        "title": [
            u"项目",
            u"日期",
            u"工时",
            u"任务",
            u"人员"
        ],
        "func": func4},
    {
        "page": u"测试明细",
        "title": [
            u"项目",
            u"日期",
            u"工时",
            u"任务",
            u"人员"
        ],
        "func": func5,
    }
]
Sheets = [
    {
        "filename": "pd_mis_pm",
        "sheets": For_Pm_Sheet
    }
]


def write_title(_book, _titles):
    _v = 0
    for _t in _titles:
        _book.write((0, _v, _t))
        _v += 1


def main():
    """
    主程序
    :return:
    """
    global Sheets, end_month

    end_month = date.today().month
    if end_month == 1:
        """New Year"""
        end_month = 12

    """创建excel文件"""
    book = exceltools.ExcelTools()
    for _sheet in Sheets:
        book.open(_sheet["filename"])
        for _sheet_page in _sheet["sheets"]:
            book.add_sheet(_sheet_page["page"])
            write_title(book, _sheet_page["title"])
            _sheet_page["func"](book)
        book.close()


if __name__ == '__main__':
    main()

