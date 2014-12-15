__author__ = 'andriusa2'

import os
import sys

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask.ext.bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.globals['DB_link'] = app.config['SQLALCHEMY_DATABASE_URI']
login_manager = LoginManager(app=app)

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

@app.errorhandler(404)
def not_found(error):
    return 'Lol, 404', 404

from app.questions.views import mod as questionsMod
app.register_blueprint(questionsMod)

from app.admin.views import mod as adminMod
app.register_blueprint(adminMod)