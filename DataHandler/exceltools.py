# -*- coding: utf-8 -*-
#
#   Excel文件服务
#   ================
#   2019.8.1 @Chengdu
#
#

import xlwt


class ExcelTools:

    def __init__(self):
        self.filename = None
        self.book = None
        self.sheet = None

    def open(self, filename):
        _fn = filename.split('.')[0]
        self.filename = _fn + ".xls"
        self.book = xlwt.Workbook()

    def add_sheet(self, sheet_name):
        self.sheet = self.book.add_sheet(sheet_name)

    def write(self, mess):
        """
        写数据项，行列从(0,0)开始
        :param mess: 序列（行号，列号，单元信息），如(0,0,u"第一个数据项名称")
        :return:
        """
        self.sheet.write(mess[0], mess[1], mess[2])

    def close(self):
        self.book.save(self.filename)


#
#