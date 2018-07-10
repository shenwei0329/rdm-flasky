#coding=utf-8

from __future__ import unicode_literals

from flask import render_template, redirect, request, url_for, flash
from . import main
from flask_login import current_user
from ..auth import server
import datetime
from ..models import Role
from ..auth import handler
import sys
from ..auth import redis_class

reload(sys)
sys.setdefaultencoding('utf-8')

my_context = None
set_time = None

"""所有内容的"正文"都通过Redis获取，"正文"由数据分析处理的中间层生成并放入。
   缓存的"正文"数据应该是全集的（由权限控制具体展现内容）
"""
# 主页面“正文”缓存
key_index = redis_class.KeyLiveClass('index')
# 研发管理“正文”缓存
key_rdm = redis_class.KeyLiveClass('rdm')
# 产品管理"正文"缓存
key_product = redis_class.KeyLiveClass('product')
# 在研产品"正文"缓存
key_product_ing = redis_class.KeyLiveClass('product_ing')
key_product_select = redis_class.KeyLiveClass('product_ing_select')
# 项目管理"正文"缓存
key_project = redis_class.KeyLiveClass('project')
# 光荣榜"正文"缓存
key_honor = redis_class.KeyLiveClass('honor')
key_honor_3m = redis_class.KeyLiveClass('honor_3m')
# 管理员"正文"缓存
key_manage = redis_class.KeyLiveClass('manage')


def get_context(key):

    _context = key.get()
    _role = Role.query.filter_by(name=current_user.username).first()
    print(">>> role.level = %d" % _role.level)
    _context['user'] = {'role': _role.level}

    return _context


@main.route('/')
def index():
    global my_context, set_time

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('index.html', **get_context(key_index))


@main.route('/rdm')
def rdm():
    global my_context, set_time

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('rdm.html', **get_context(key_rdm))


@main.route('/product')
def product():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('product.html', **get_context(key_product))


@main.route('/producting')
def producting():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('producting.html', **get_context(key_product_ing))


@main.route('/pd_select/<value>')
def pd_select(value):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    """
    _desc = handler.get_pd_project_desc(value)
    _context = server.set_pding_context()
    _context['pd_code'] = value.lower()
    _context['pd_landmark'] = u"%s" % _desc[u'里程碑']
    _context['pd_step'] = u"%s" % _desc[u'当前阶段']
    _context['total_task'] = _desc[u'任务总数']
    _context['ed_task'] = _desc[u'已完成任务数']
    _context['ratio'] = _desc[u'任务完成率']
    _context['personals'] = handler.get_personal_stat(value)

    role = Role.query.filter_by(name=current_user.username).first()
    print(">>> role.level = %d" % role.level)
    _context['user'] = {'role': role.level}
    """
    return render_template('product_desc.html', **get_context(key_product_select[value]))


@main.route('/project')
def project():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    """
    role = Role.query.filter_by(name=current_user.username).first()
    _pj = handler.get_project_info('pj_deliver_t')
    _val = handler.get_project_info('pj_ing_t')
    _imp_pj = handler.get_imp_projects()
    _pj_managers = handler.get_pj_managers()
    context = dict(
        user={"role": role.level},
        projects=_pj,
        pj_count=len(_pj),
        pre_projects=_val,
        pre_pj_count=len(_val),
        pre_quota=handler.get_sum(_val, u'规模'),
        imp_projects=_imp_pj,
        pj_managers=_pj_managers,
        pj_manager_count=len(_pj_managers),
    )
    role = Role.query.filter_by(name=current_user.username).first()
    print(">>> role.level = %d" % role.level)
    context['user'] = {'role': role.level}
    """
    return render_template('project.html', **get_context(key_project))


@main.route('/honor')
def honor():
    global my_context, set_time

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    """
    _context = server.set_honor_context(None, None)
    role = Role.query.filter_by(name=current_user.username).first()
    print(">>> role.level = %d" % role.level)
    _context['user'] = {'role': role.level}
    _context['info'] = u"【本年度】"
    """
    return render_template('honor.html', **get_context(key_honor))


@main.route('/honor_select/<value>')
def honor_select(value):

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    """
    print(">>> value: %s" % value)

    if value in 'yearly':
        _context = server.set_honor_context(None, None)
        _context['info'] = u"【本年度】"
    elif value in 'monthly':
        _v = handler.cal_date_monthly(3)
        _st_date = _v['st_date']
        _ed_date = _v['ed_date']
        _context = server.set_honor_context(_st_date, _ed_date)
        _context['info'] = u"【近三个月】"
    else:
        _context = server.set_honor_context('2018-06-04', '2018-06-11')
        _context['info'] = u"【上周】"

    role = Role.query.filter_by(name=current_user.username).first()
    print(">>> role.level = %d" % role.level)
    _context['user'] = {'role': role.level}
    """
    if value in 'yearly':
        return render_template('honor_desc.html', **get_context(key_honor))
    return render_template('honor_desc.html', **get_context(key_honor_3m))


@main.route('/manager')
def manager():

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    """
    _context = server.set_manager_context()
    """
    return render_template('manager.html', **get_context(key_manage))
