from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

import dbconfig
from werkzeug.utils import secure_filename




app = Flask(__name__)

if dbconfig.debug:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}@{}/danceapp'\
        .format(dbconfig.db_user,
                dbconfig.db_hostname)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}:{}/{}'\
        .format(dbconfig.db_user,
                dbconfig.db_password,
                dbconfig.db_hostname,
                dbconfig.db_port,
                dbconfig.db_name)


UPLOAD_FOLDER = 'danceapp/static'
ALLOWED_EXTENSIONS = set([ 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

import danceapp.views
import danceapp.filters
import danceapp.plugin_filters
import danceapp.models
import danceapp.logger
from danceapp.plugins import load_plugins

load_plugins()



BCRYPT_LOG_ROUNDS = 12

from flask_login import LoginManager
from models import User


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =  "signin"



@login_manager.user_loader
def load_user(userid):
    return User.query.filter(User.id==userid).first()
