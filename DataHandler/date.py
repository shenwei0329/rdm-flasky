# -*- coding: utf-8 -*-
#
#


class DateObject:

    def __init__(self):
        self.date_link = {}
        self.sum_counter = 0

    def add(self, date, obj):
        if date not in self.date_link:
            self.date_link[date] = {}
        _obj = obj
        if ',' in obj:
            _obj = obj.split(',')
        if u"，" in obj:
            _obj = obj.split(u'，')

        if _obj != obj:
            for _o in _obj:
                if _o not in self.date_link[date]:
                    self.date_link[date][_o] = 0
                self.date_link[date][_o] += 1
        else:
            if '20' not in obj:
                if obj not in self.date_link[date]:
                    self.date_link[date][obj] = 0
                self.date_link[date][obj] += 1
        self.sum_counter += 1

    def stat(self):
        return self.date_link

    def get_sum(self):
        return self.sum_counter


def get_date(date):
    _date = date
    if "T" in date:
        _date = _date.split('T')[0]
    if " " in date:
        _date = _date.split(' ')[0]
    if u"年" in _date:
        _date = _date.replace(u"年", '-').replace(u"月", '-').replace(u"日", '')
    if "-" in _date:
        _v = _date.split('-')
        if len(_v) == 3:
            _date = "%04d%02d%02d" % (int(_v[0]), int(_v[1]), int(_v[2]))
        else:
            _date = "20180101"
    # print(">>>get_date<<<[%s][%s]" % (date, _date))
    return _date

