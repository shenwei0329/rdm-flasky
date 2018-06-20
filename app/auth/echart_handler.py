#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
#
#   PyeCharts服务程序集
#   ===================
#   2018.5.10 @Chengdu
#
#

from __future__ import unicode_literals


def get_geo(title, sub_title, addr_data):
    from pyecharts import Geo

    data = []

    for _data in addr_data:
        if _data not in [u'上海', u'成都', u'西安', u'温州', u'南京', u'石家庄', u'嘉兴',
                         u'北京', u'南昌', u'福州', u'大连', u'武汉', u'呼和浩特',
                         u'合肥', u'南宁', u'杭州', u'贵阳', u'深圳', u'沈阳',
                         u'重庆', u'昆明', u'哈尔滨', u'天津', u'乌鲁木齐', u'拉萨',
                         u'海口', u'三亚', u'东莞', u'大理', u'葫芦岛', u'无锡', u'榆林',
                         u'西昌', u'德阳', u'长沙', u'锦州', u'秦皇岛', u'珠海', u'广州',
                         u'太原', u'银川']:
            print _data,
            continue
        data.append((_data, addr_data[_data]),)

    print ">"

    # print data

    geo = Geo(title, sub_title,
              title_color="#fff",
              title_pos="center",
              width=320,
              height=240,
              background_color='#404a59')

    attr, value = geo.cast(data)
    for _v in attr:
        print u"[%s]" % _v,
    print "|"

    geo.add("", attr, value, visual_range=[0, 10], visual_text_color="#fff", symbol_size=15, is_visualmap=True)
    # geo.show_config()
    geo.options['toolbox']['show'] = False
    return geo.render_embed()


def bar(title, attr, datas):
    from pyecharts import Bar

    # bar
    # attr = ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"]
    # v1 = [5, 20, 36, 10, 75, 90]
    # v2 = [10, 25, 8, 60, 20, 80]
    bar = Bar(title,
              width=320,
              height=180,
              title_pos="center",
              background_color='#b0bab9',
              )
    for _d in datas:
        bar.add(_d['title'],
                attr,
                _d['data'],
                is_stack=False,
                legend_top='bottom',
                mark_line=['average'],
                mark_point=['max', 'min'])

    bar.options['toolbox']['show'] = False
    return bar.render_embed()


def effectscatter(title, datas, size=None):
    from pyecharts import EffectScatter

    # import random
    # data = [random.randint(0, 100) for _ in range(80)]
    range_color = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf',
                   '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']

    if size is None:
        scatter = EffectScatter(
                                title,
                                width=320,
                                height=180,
                                title_pos="center",
                                background_color='#b0bab9',
                          )
    else:
        scatter = EffectScatter(
                                title,
                                width=size['width'],
                                height=size['height'],
                                title_pos="center",
                                background_color='#b0bab9',
                          )
    _scale = 1.5
    for _data in datas:
        if "v" not in _data:
            scatter.add("", _data['x'], _data['y'],
                        is_visualmap=False,
                        visual_range_color=range_color,
                        mark_line=['average'],
                        mark_point=['max', 'min'],
                        effect_scale=_scale,
                        symbol_size=5,
                        )
            _scale += 1.
        else:
            scatter.add("", _data['x'], _data['y'],
                        is_visualmap=False,
                        # visual_range_color=range_color,
                        mark_line=['average'],
                        mark_point=['max', 'min'],
                        effect_scale=1.5 + float(_data['v'])/40.,
                        symbol_size=3+_data['v']/3,
                        )

    scatter.options['toolbox']['show'] = False
    return scatter.render_embed()


def effectscatterByInd(title, datas, size=None):
    from pyecharts import EffectScatter

    # import random
    # data = [random.randint(0, 100) for _ in range(80)]
    range_color = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf',
                   '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']

    if size is None:
        scatter = EffectScatter(
                                title,
                                width=320,
                                height=180,
                                title_pos="center",
                                background_color='#b0bab9',
        )
    else:
        scatter = EffectScatter(
                                title,
                                width=size['width'],
                                height=size['height'],
                                title_pos="center",
                                background_color='#b0bab9',
        )

    for _val in datas:

        # print(">>> _val = %s" % _val)
        _effect_scale = 3.
        _symbol_size = 3.
        if "high" in _val:
            _effect_scale += 1.5
            _symbol_size += 8.
        elif "norm" in _val:
            _effect_scale += 1.
            _symbol_size += 5.

        scatter.add("", datas[_val]['x'], datas[_val]['y'],
                    is_visualmap=False,
                    visual_range_color=range_color,
                    mark_line=['average'],
                    mark_point=['max', 'min'],
                    effect_scale=_effect_scale,
                    symbol_size=_symbol_size,
                    legend_top='bottom',
                    )

    scatter.options['toolbox']['show'] = False
    scatter.options['xAxis'][0]['show'] = False
    scatter.options['yAxis'][0]['show'] = False
    return scatter.render_embed()


def scatter(title, range_def, data, size=None):
    from pyecharts import Scatter

    # import random
    # data = [random.randint(0, 100) for _ in range(80)]
    range_color = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf',
                   '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']

    if size is None:
        scatter = Scatter(title,
                          width=320,
                          height=180,
                          title_pos="center",
                          background_color='#b0bab9',
                          )
    else:
        scatter = Scatter(title,
                          width=size['width'],
                          height=size['height'],
                          title_pos="center",
                          background_color='#b0bab9',
                          )

    scatter.add("", range(len(data)), data,
                visual_range=range_def,
                is_visualmap=False,
                visual_range_color=range_color,
                mark_line=['average'],
                mark_point=['max', 'min'])

    scatter.options['toolbox']['show'] = False
    return scatter.render_embed()


def scatter3d():
    from pyecharts import Scatter3D

    import random
    data = [[random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)] for _ in range(80)]
    range_color = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf',
                   '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
    scatter3D = Scatter3D(u"【人-任务-日期】分布图", width=600, height=600)
    scatter3D.add("", data, is_visualmap=True, visual_range_color=range_color)

    scatter3D.options['toolbox']['show'] = False
    return scatter3D.render_embed()


def line(title, data):
    """
    画线
    :param title:
    :param data:
    :return:
    """

    """ '#0f000000',"""
    from pyecharts import Line

    line = Line(title,
                title_pos="center",
                )
    for _dot in data:
        line.add(_dot['title'],
                 _dot['attr'],
                 _dot['data'],
                 is_fill=True,
                 line_opacity=0.8,
                 area_color=_dot['color'],
                 area_opacity=0.4,
                 is_smooth=True)

    line.options['toolbox']['show'] = False
    return line.render_embed()


def pie(title, attr, values):
    """
    输出Pie图
    :param title: 标题
    :param attr: 属性
    :param values: 数据
    :return: 图形
    """
    from pyecharts import Pie

    pie = Pie(title, title_pos='center', width=300)
    for _value in values:
        pie.add(title, attr, _value,
                center=[50, 50],
                is_random=False,
                radius=[20, 45],
                rosetype='rose',
                is_legend_show=False,
                is_label_show=True,
                background_color='#b0bab9',
                label_text_size=12)

    pie.options['toolbox']['show'] = False

    return pie.render_embed()

