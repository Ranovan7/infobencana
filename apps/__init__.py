from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_moment import Moment
import os

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = f"{os.getcwd()}/apps/static/uploaded_photos/"
# app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True    # easier json reading
db = SQLAlchemy(app)

''' Putting Managers '''
moment = Moment()
login = LoginManager()
login.login_view = 'core.login'

login.init_app(app)
moment.init_app(app)

'''Import Blueprints'''
from apps.kejadian import bp as admin_bp
from apps.api import bp as api_bp
from apps.core import bp as main_bp

app.register_blueprint(main_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(api_bp, url_prefix='/api')
