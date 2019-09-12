# -*- coding: utf-8 -*-
#
#   生成数据文件，并通过邮件发送
#   ============================
#   2019.8.1 @Chengdu
#

from DataHandler import exceltools
from DataHandler import xlsx_class
import random

line_number = 1


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
    global line_number

    """读取excel文件"""
    input = xlsx_class.xlsx_handler("pj_work_daily.xls")
    input_sample = xlsx_class.xlsx_handler("pj_work_daily_sample.xls")

    """创建excel文件"""
    # """
    book = exceltools.ExcelTools()
    book.open("pj_work_daily_sum")
    book.add_sheet(u"工作日志")
    write_title(book, [u"日期", u"人员", u"内容", u"工时"])
    # """
    input.setSheet(0)
    input_sample.setSheet(0)
    rows = input_sample.getNrows()
    for _i in range(rows):
        if _i == 0:
            continue
        row = input.getXlsxRow(_i, 4, None)
        row_sample = input_sample.getXlsxRow(_i, 4, None)
        print row_sample
        book.write((_i, 0, row_sample[0]))
        book.write((_i, 1, row_sample[1]))
        book.write((_i, 2, row[2]))
        book.write((_i, 3, row_sample[3]))

    # """
    book.close()
    # """


if __name__ == '__main__':
    main()

