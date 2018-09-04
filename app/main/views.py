#coding=utf-8

from __future__ import unicode_literals

from flask import render_template, redirect, url_for
from . import main
from flask_login import current_user
from ..models import Role
import sys
from ..auth import redis_class

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


def get_context(key):

    _context = key.get()
    _role = Role.query.filter_by(name=current_user.username).first()
    print(">>> role.level = %d" % _role.level)
    _context['user'] = {'role': _role.level}

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
