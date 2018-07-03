#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
#
#   PyeCharts服务程序集
#   ===================
#   2018.5.10 @Chengdu
#
#

from __future__ import unicode_literals

from pyecharts import Sankey, Page, Style, Boxplot


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


def boxplot(title, datas, size=None):

    if size is None:
        scatter = Boxplot(
                                title,
                                width=320,
                                height=180,
                                title_pos="center",
                                background_color='#f0f0f0',
                          )
    else:
        scatter = Boxplot(
                                title,
                                width=size['width'],
                                height=size['height'],
                                title_pos="center",
                                background_color='#f0f0f0',
                          )
    _values = {}
    for _data in datas:
        _idx = 0
        for _x in _data['x']:
            if _x not in _values:
                _values[_x] = []
            _values[_x].append(_data['y'][_idx])
            _idx += 1

    _x = []
    _y = []
    for _v in _values:
        _x.append(_v)
        _y.append(_values[_v])

    scatter.add("", _x, _y,
                is_visualmap=False,
                mark_line=['average'],
                mark_point=['max', 'min'],
                )

    scatter.options['yAxis'][0]['splitArea'] = True
    scatter.options['xAxis'][0]['splitArea'] = False
    scatter.options['toolbox']['show'] = False
    return scatter.render_embed()


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
                                background_color='#f0f0f0',
                          )
    else:
        scatter = EffectScatter(
                                title,
                                width=size['width'],
                                height=size['height'],
                                title_pos="center",
                                background_color='#f0f0f0',
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
                                background_color='#f0f0f0',
        )
    else:
        scatter = EffectScatter(
                                title,
                                width=size['width'],
                                height=size['height'],
                                title_pos="center",
                                background_color='#f0f0f0',
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

ENERGY = {
    "nodes": [
        {
            "name": "Agricultural 'waste'"
        },
        {
            "name": "Bio-conversion"
        },
        {
            "name": "Liquid"
        },
        {
            "name": "Losses"
        },
        {
            "name": "Solid"
        },
        {
            "name": "Gas"
        },
        {
            "name": "Biofuel imports"
        },
        {
            "name": "Biomass imports"
        },
        {
            "name": "Coal imports"
        },
        {
            "name": "Coal"
        },
        {
            "name": "Coal reserves"
        },
        {
            "name": "District heating"
        },
        {
            "name": "Industry"
        },
        {
            "name": "Heating and cooling - commercial"
        },
        {
            "name": "Heating and cooling - homes"
        },
        {
            "name": "Electricity grid"
        },
        {
            "name": "Over generation / exports"
        },
        {
            "name": "H2 conversion"
        },
        {
            "name": "Road transport"
        },
        {
            "name": "Agriculture"
        },
        {
            "name": "Rail transport"
        },
        {
            "name": "Lighting & appliances - commercial"
        },
        {
            "name": "Lighting & appliances - homes"
        },
        {
            "name": "Gas imports"
        },
        {
            "name": "Ngas"
        },
        {
            "name": "Gas reserves"
        },
        {
            "name": "Thermal generation"
        },
        {
            "name": "Geothermal"
        },
        {
            "name": "H2"
        },
        {
            "name": "Hydro"
        },
        {
            "name": "International shipping"
        },
        {
            "name": "Domestic aviation"
        },
        {
            "name": "International aviation"
        },
        {
            "name": "National navigation"
        },
        {
            "name": "Marine algae"
        },
        {
            "name": "Nuclear"
        },
        {
            "name": "Oil imports"
        },
        {
            "name": "Oil"
        },
        {
            "name": "Oil reserves"
        },
        {
            "name": "Other waste"
        },
        {
            "name": "Pumped heat"
        },
        {
            "name": "Solar PV"
        },
        {
            "name": "Solar Thermal"
        },
        {
            "name": "Solar"
        },
        {
            "name": "Tidal"
        },
        {
            "name": "UK land based bioenergy"
        },
        {
            "name": "Wave"
        },
        {
            "name": "Wind"
        }
    ],
    "links": [
        {
            "source": "Agricultural 'waste'",
            "target": "Bio-conversion",
            "value": 124.729
        },
        {
            "source": "Bio-conversion",
            "target": "Liquid",
            "value": 0.597
        },
        {
            "source": "Bio-conversion",
            "target": "Losses",
            "value": 26.862
        },
        {
            "source": "Bio-conversion",
            "target": "Solid",
            "value": 280.322
        },
        {
            "source": "Bio-conversion",
            "target": "Gas",
            "value": 81.144
        },
        {
            "source": "Biofuel imports",
            "target": "Liquid",
            "value": 35
        },
        {
            "source": "Biomass imports",
            "target": "Solid",
            "value": 35
        },
        {
            "source": "Coal imports",
            "target": "Coal",
            "value": 11.606
        },
        {
            "source": "Coal reserves",
            "target": "Coal",
            "value": 63.965
        },
        {
            "source": "Coal",
            "target": "Solid",
            "value": 75.571
        },
        {
            "source": "District heating",
            "target": "Industry",
            "value": 10.639
        },
        {
            "source": "District heating",
            "target": "Heating and cooling - commercial",
            "value": 22.505
        },
        {
            "source": "District heating",
            "target": "Heating and cooling - homes",
            "value": 46.184
        },
        {
            "source": "Electricity grid",
            "target": "Over generation / exports",
            "value": 104.453
        },
        {
            "source": "Electricity grid",
            "target": "Heating and cooling - homes",
            "value": 113.726
        },
        {
            "source": "Electricity grid",
            "target": "H2 conversion",
            "value": 27.14
        },
        {
            "source": "Electricity grid",
            "target": "Industry",
            "value": 342.165
        },
        {
            "source": "Electricity grid",
            "target": "Road transport",
            "value": 37.797
        },
        {
            "source": "Electricity grid",
            "target": "Agriculture",
            "value": 4.412
        },
        {
            "source": "Electricity grid",
            "target": "Heating and cooling - commercial",
            "value": 40.858
        },
        {
            "source": "Electricity grid",
            "target": "Losses",
            "value": 56.691
        },
        {
            "source": "Electricity grid",
            "target": "Rail transport",
            "value": 7.863
        },
        {
            "source": "Electricity grid",
            "target": "Lighting & appliances - commercial",
            "value": 90.008
        },
        {
            "source": "Electricity grid",
            "target": "Lighting & appliances - homes",
            "value": 93.494
        },
        {
            "source": "Gas imports",
            "target": "Ngas",
            "value": 40.719
        },
        {
            "source": "Gas reserves",
            "target": "Ngas",
            "value": 82.233
        },
        {
            "source": "Gas",
            "target": "Heating and cooling - commercial",
            "value": 0.129
        },
        {
            "source": "Gas",
            "target": "Losses",
            "value": 1.401
        },
        {
            "source": "Gas",
            "target": "Thermal generation",
            "value": 151.891
        },
        {
            "source": "Gas",
            "target": "Agriculture",
            "value": 2.096
        },
        {
            "source": "Gas",
            "target": "Industry",
            "value": 48.58
        },
        {
            "source": "Geothermal",
            "target": "Electricity grid",
            "value": 7.013
        },
        {
            "source": "H2 conversion",
            "target": "H2",
            "value": 20.897
        },
        {
            "source": "H2 conversion",
            "target": "Losses",
            "value": 6.242
        },
        {
            "source": "H2",
            "target": "Road transport",
            "value": 20.897
        },
        {
            "source": "Hydro",
            "target": "Electricity grid",
            "value": 6.995
        },
        {
            "source": "Liquid",
            "target": "Industry",
            "value": 121.066
        },
        {
            "source": "Liquid",
            "target": "International shipping",
            "value": 128.69
        },
        {
            "source": "Liquid",
            "target": "Road transport",
            "value": 135.835
        },
        {
            "source": "Liquid",
            "target": "Domestic aviation",
            "value": 14.458
        },
        {
            "source": "Liquid",
            "target": "International aviation",
            "value": 206.267
        },
        {
            "source": "Liquid",
            "target": "Agriculture",
            "value": 3.64
        },
        {
            "source": "Liquid",
            "target": "National navigation",
            "value": 33.218
        },
        {
            "source": "Liquid",
            "target": "Rail transport",
            "value": 4.413
        },
        {
            "source": "Marine algae",
            "target": "Bio-conversion",
            "value": 4.375
        },
        {
            "source": "Ngas",
            "target": "Gas",
            "value": 122.952
        },
        {
            "source": "Nuclear",
            "target": "Thermal generation",
            "value": 839.978
        },
        {
            "source": "Oil imports",
            "target": "Oil",
            "value": 504.287
        },
        {
            "source": "Oil reserves",
            "target": "Oil",
            "value": 107.703
        },
        {
            "source": "Oil",
            "target": "Liquid",
            "value": 611.99
        },
        {
            "source": "Other waste",
            "target": "Solid",
            "value": 56.587
        },
        {
            "source": "Other waste",
            "target": "Bio-conversion",
            "value": 77.81
        },
        {
            "source": "Pumped heat",
            "target": "Heating and cooling - homes",
            "value": 193.026
        },
        {
            "source": "Pumped heat",
            "target": "Heating and cooling - commercial",
            "value": 70.672
        },
        {
            "source": "Solar PV",
            "target": "Electricity grid",
            "value": 59.901
        },
        {
            "source": "Solar Thermal",
            "target": "Heating and cooling - homes",
            "value": 19.263
        },
        {
            "source": "Solar",
            "target": "Solar Thermal",
            "value": 19.263
        },
        {
            "source": "Solar",
            "target": "Solar PV",
            "value": 59.901
        },
        {
            "source": "Solid",
            "target": "Agriculture",
            "value": 0.882
        },
        {
            "source": "Solid",
            "target": "Thermal generation",
            "value": 400.12
        },
        {
            "source": "Solid",
            "target": "Industry",
            "value": 46.477
        },
        {
            "source": "Thermal generation",
            "target": "Electricity grid",
            "value": 525.531
        },
        {
            "source": "Thermal generation",
            "target": "Losses",
            "value": 787.129
        },
        {
            "source": "Thermal generation",
            "target": "District heating",
            "value": 79.329
        },
        {
            "source": "Tidal",
            "target": "Electricity grid",
            "value": 9.452
        },
        {
            "source": "UK land based bioenergy",
            "target": "Bio-conversion",
            "value": 182.01
        },
        {
            "source": "Wave",
            "target": "Electricity grid",
            "value": 19.013
        },
        {
            "source": "Wind",
            "target": "Electricity grid",
            "value": 289.366
        }
    ]
}


def create_charts():
    page = Page()

    style = Style(
        width=800, height=800,
        background_color='#b0bab9',
    )

    nodes = [
        {'name': 'category1'}, {'name': 'category2'}, {'name': 'category3'},
        {'name': 'category4'}, {'name': 'category5'}, {'name': 'category6'},
    ]

    links = [
        {'source': 'category1', 'target': 'category3', 'value': 10},
        {'source': 'category2', 'target': 'category3', 'value': 20},
        {'source': 'category3', 'target': 'category4', 'value': 10},
        {'source': 'category4', 'target': 'category5', 'value': 15},
        {'source': 'category3', 'target': 'category5', 'value': 10},
        {'source': 'category4', 'target': 'category6', 'value': 2},
        {'source': 'category3', 'target': 'category6', 'value': 10}
    ]
    chart = Sankey("桑基图-默认", **style.init_style)
    chart.add("sankey", nodes, links, line_opacity=0.2,
              line_curve=0.5, line_color='source', is_label_show=True,
              label_pos='right')
    chart.options['toolbox']['show'] = False
    page.add(chart)

    chart = Sankey("桑基图-自定义", **style.init_style)
    chart.add("sankey", nodes=ENERGY['nodes'], links=ENERGY['links'],
              line_opacity=0.2, line_curve=0.5, line_color='source',
              is_label_show=True, label_pos='right')
    chart.options['toolbox']['show'] = False
    page.add(chart)

    return page.render_embed()


def sankey_charts(title, nodes, links):

    style = Style(
        width=1200, height=800,
        background_color='#f0f0f0',
    )
    chart = Sankey(title, **style.init_style)
    chart.add("", nodes, links, line_opacity=0.2,
              line_curve=0.5, line_color='source', is_label_show=True,
              label_pos='right')
    chart.options['toolbox']['show'] = False
    return chart.render_embed()
