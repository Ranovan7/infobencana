from flask import render_template
from app.main import bp

from app.models import Kejadian

@bp.route('/')
def index():
    return render_template('index.html', title='Info Kejadian')


@bp.route('/map')
def map():
    kjds = Kejadian.select()
    return render_template('map.html', kejadian=kjds)


@bp.route('/add')
def add():
    return render_template('add.html')
