#coding=utf-8

from __future__ import unicode_literals

from flask import render_template, redirect, url_for
from . import main
from flask_login import current_user
from ..models import Role
import sys
from ..auth import redis_class
import logging

reload(sys)
sys.setdefaultencoding('utf-8')

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
key_product_select_FAST = redis_class.KeyLiveClass('product_ing_select.FAST')
key_product_select_HUBBLE = redis_class.KeyLiveClass('product_ing_select.HUBBLE')
# 项目管理"正文"缓存
key_project = redis_class.KeyLiveClass('project')
# 光荣榜"正文"缓存
key_honor = redis_class.KeyLiveClass('honor')
key_honor_3m = redis_class.KeyLiveClass('honor_3m')
# 管理员"正文"缓存
key_manage = redis_class.KeyLiveClass('manage')
# 个人档案
key_personal = redis_class.KeyLiveClass('personal')

"""个人统计数据"""
key_member_checkon = redis_class.KeyLiveClass('member_checkon')

"""邮箱"""
key_email = redis_class.KeyLiveClass('email')


def get_context(key, data=None):

    _context = key.get()
    _email = key_email.get()
    _context['email'] = _email['email']
    _role = Role.query.filter_by(name=current_user.email).first()
    print(">>> role.level = %d" % _role.level)
    _context['user'] = {'role': _role.level}

    if current_user.email in _email['email']:
        _context['username'] = _email['email'][current_user.email]
    else:
        _context['username'] = current_user.username
        if 'userindex' in _context:
            """清除原有的内容"""
            _context.pop('userindex')

    _context['reportDate'] = key_index.get()['reportDate']
    if data is not None:
        _context['value'] = data
    print(">>> reportDate[%s]" % _context['reportDate'])
    _context['len'] = len
    _context['range'] = range
    _context['int'] = int
    _context['sorted'] = sorted

    return _context


def get_contexts(keys, data=None):

    _context = keys[0].get()
    _email = key_email.get()
    _context['email'] = _email['email']
    for _key in keys[1:]:
        __context = _key.get()
        for _key in __context:
            print(">>> get_contexts: _key = %s" % _key)
            _context[_key] = __context[_key]

    _role = Role.query.filter_by(name=current_user.email).first()
    print(">>> role.level = %d" % _role.level)
    _context['user'] = {'role': _role.level}

    if current_user.email in _email['email']:
        _context['username'] = _email['email'][current_user.email]
    else:
        _context['username'] = current_user.username
        if 'userindex' in _context:
            """清除原有的内容"""
            _context.pop('userindex')

    _context['reportDate'] = key_index.get()['reportDate']
    if data is not None:
        _context['value'] = data
        if "members" in _context:
            _context['my'] = _context["members"][int(data)]
    print(">>> reportDate[%s]" % _context['reportDate'])
    _context['len'] = len
    _context['range'] = range
    _context['int'] = int
    _context['sorted'] = sorted

    return _context


@main.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('index.html', **get_context(key_index))


@main.route('/rdm')
def rdm():
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

    print value

    if value.upper() == 'FAST':
        return render_template('product_desc.html', **get_context(key_product_select_FAST))
    else:
        return render_template('product_desc.html', **get_context(key_product_select_HUBBLE))


@main.route('/project')
def project():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('project.html', **get_context(key_project))


@main.route('/honor')
def honor():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('honor.html', **get_context(key_honor))


@main.route('/honor_select/<value>')
def honor_select(value):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if value in 'yearly':
        return render_template('honor_desc.html', **get_context(key_honor))
    return render_template('honor_desc.html', **get_context(key_honor_3m))


@main.route('/manager')
def manager():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('manager.html', **get_context(key_manage))


@main.route('/finance')
def finance():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('finance.html', **get_context(key_rdm))


@main.route('/finance_tc_select/<value>')
def finance_tc_select(value):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    logging.log(logging.WARN, ">>> finance_tc_select <%s>" % value)
    return render_template('finance_tc_select.html', **get_context(key_rdm, data=value))


@main.route('/finance_pd_pj_select/<value>')
def finance_pd_pj_select(value):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    logging.log(logging.WARN, ">>> finance_pd_pj_select <%s>" % value)
    return render_template('finance_pd_pj_select.html', **get_context(key_rdm, data=value))


@main.route('/finance_select/<value>')
def finance_select(value):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('honor_desc.html', **get_context(key_rdm))


@main.route('/personal')
def personal():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('personal.html', **get_contexts([key_personal, key_member_checkon]))


@main.route('/member_select/<value>')
def member_select(value):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('personal_desc.html', **get_contexts([key_personal, key_member_checkon], data=value))


@main.route('/evaluation')
def evaluation():
    """
    评定与评估
    :return:
    """
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('evaluation.html', **get_context(key_personal))


