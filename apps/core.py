from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user
from apps.forms import LoginForm
from apps.models import Kejadian, User
from sqlalchemy import desc, extract
from datetime import datetime
import os
import json

bp = Blueprint('core', __name__)

kalender = [
    'Pilih',
    'Januari',
    'Februari',
    'Maret',
    'April',
    'Mei',
    'Juni',
    'Juli',
    'Agustus',
    'September',
    'Oktober',
    'November',
    'Desember',
]


@bp.route('/')
def index():
    all_kejadian = Kejadian.query.filter(Kejadian.dampakdesa.any())
    results = {}
    for kejadian in all_kejadian:
        year = kejadian.waktu.year
        if year not in results:
            results[year] = 0
        results[year] += 1
    info = []
    for year in results:
        info.append(
            {
                'tahun': year,
                'jumlah': results[year]
            }
        )
    return render_template('index.html', info=info, user=current_user)


@bp.route('/bencana/', strict_slashes=False)
def daftar_bencana():
    latest = Kejadian.query.order_by(desc(Kejadian.waktu)).first()
    year = int(request.args.get('tahun', latest.waktu.year))
    picked_kejadian = Kejadian.query.filter(
        extract('year', Kejadian.waktu) == year, Kejadian.dampakdesa.any()).order_by(
        desc(Kejadian.waktu))
    results = {}
    kejadian_count = 0
    for kejadian in picked_kejadian:
        month = kejadian.waktu.month
        if month not in results:
            results[month] = []

        results[month].append(kejadian)
        kejadian_count += 1
    info = []
    for month in results:
        info.append(
            {
                'bulan': month,
                'kejadian': results[month]
            }
        )

    # sort the info by month descending
    info.sort(key=lambda x: x['bulan'], reverse=True)

    # convert month number into month name
    for i in info:
        i['bulan'] = kalender[i['bulan']]
    # get all year option
    kjds = Kejadian.query.order_by(desc(Kejadian.waktu)).all()
    year_option = []
    for k in kjds:
        if k.waktu.year not in year_option:
            year_option.append(k.waktu.year)
    return render_template('daftar_bencana.html', info=info, user=current_user, year_option=year_option[::-1], year=year, count=kejadian_count)


@bp.route('/map', strict_slashes=False)
def map():
    kjds = Kejadian.query.order_by(desc(Kejadian.waktu)).filter(Kejadian.dampakdesa.any())
    kid = int(request.args.get('kid', 0))
    return render_template('map.html', kejadian=kjds, user=current_user, kid=kid)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    form = LoginForm()
    if form.validate_on_submit():
        # print('Form Valid')
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            # print(user.username)
            if not user.check_password(form.password.data):
                flash('Password keliru', 'danger')
                return redirect(url_for('core.login'))
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            flash('User tidak ditemukan', 'danger')
            return redirect(url_for('core.login'))
    return render_template('login.html', form=form, user=current_user)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('core.map'))
