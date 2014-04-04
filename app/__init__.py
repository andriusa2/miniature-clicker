__author__ = 'andriusa2'

import os
import sys

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('config')

login_manager = LoginManager(app=app)

db = SQLAlchemy(app)

########################
# Configure Secret Key #
########################
# def install_secret_key(app, filename='secret_key'):
#     """Configure the SECRET_KEY from a file
#     in the instance directory.
#
#     If the file does not exist, print instructions
#     to create it from a shell with a random key,
#     then exit.
#     """
#     filename = os.path.join(app.instance_path, filename)
#
#     try:
#         app.config['SECRET_KEY'] = open(filename, 'rb').read()
#     except IOError:
#         print('Error: No secret key. Create it with:')
#         full_path = os.path.dirname(filename)
#         if not os.path.isdir(full_path):
#             print('mkdir -p {filename}'.format(filename=full_path))
#         print('head -c 24 /dev/urandom > {filename}'.format(filename=full_path))
#         sys.exit(1)

# if not app.config['DEBUG']:
#     install_secret_key(app)

@app.errorhandler(404)
def not_found(error):
    return 'Lol, 404', 404

from app.questions.views import mod as questionsMod
app.register_blueprint(questionsMod)
from app.admin.views import mod as adminMod
app.register_blueprint(adminMod)
# Later on you'll import the other blueprints the same way:
#from app.comments.views import mod as commentsModule
#from app.posts.views import mod as postsModule
#app.register_blueprint(commentsModule)
#app.register_blueprint(postsModule)