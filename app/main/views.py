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

reload(sys)
sys.setdefaultencoding('utf-8')

my_context = None
honor_context = None
set_time = None


@main.route('/')
def index():
    global my_context, set_time, honor_context

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if my_context is None:
        my_context = server.set_context()
        set_time = datetime.datetime.now()
        honor_context = server.set_honor_context()
    elif (datetime.datetime.now() - set_time).seconds > 3600*8:
        set_time = datetime.datetime.now()
        my_context = server.set_context()
        honor_context = server.set_honor_context()
    role = Role.query.filter_by(name=current_user.username).first()
    print(">>> role.level = %d" % role.level)
    my_context['user'] = {'role': role.level}

    return render_template('index.html', **my_context)


@main.route('/rdm')
def rdm():
    global my_context, set_time

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if my_context is None:
        my_context = server.set_context()
        set_time = datetime.datetime.now()

    _context = server.set_rdm_context()
    return render_template('rdm.html', **_context)


@main.route('/product')
def product():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    _context = server.set_pd_context()
    return render_template('product.html', **_context)


@main.route('/producting')
def producting():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    _context = server.set_pding_context()
    return render_template('producting.html', **_context)


@main.route('/pd_select/<value>')
def pd_select(value):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    _desc = handler.get_pd_project_desc(value)
    _context = server.set_pding_context()
    _context['pd_code'] = value.lower()
    _context['pd_landmark'] = u"%s" % _desc[u'里程碑']
    _context['pd_step'] = u"%s" % _desc[u'当前阶段']
    _context['total_task'] = _desc[u'任务总数']
    _context['ed_task'] = _desc[u'已完成任务数']
    _context['ratio'] = _desc[u'任务完成率']
    _context['personals'] = handler.get_personal_stat(value)

    return render_template('product_desc.html', **_context)


@main.route('/project')
def project():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    role = Role.query.filter_by(name=current_user.username).first()
    _pj = handler.get_project_info('pj_deliver_t')
    _val = handler.get_project_info('pj_ing_t')
    context = dict(
        user={"role": role.level},
        projects=_pj,
        pj_count=len(_pj),
        pre_projects=_val,
        pre_pj_count=len(_val),
        pre_quota=handler.get_sum(_val, u'规模'),
    )

    return render_template('project.html', **context)


@main.route('/honor')
def honor():
    global my_context, set_time, honor_context

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if my_context is None:
        my_context = server.set_context()
        set_time = datetime.datetime.now()
    if honor_context is None:
        honor_context = server.set_honor_context()

    return render_template('honor.html', **honor_context)
