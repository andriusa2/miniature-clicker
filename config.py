import os
from sqlalchemy import create_engine
_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

ADMINS = frozenset(['youremail@yourdomain.com'])
SECRET_KEY = 'This string will be replaced with a proper key in production.'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'app.db')
# SQLALCHEMY_DATABASE_URL = 'sqlite://'  # in memory
DATABASE_CONNECT_OPTIONS = {}
# SQLALCHEMY_ECHO = True

THREADS_PER_PAGE = 8

CSRF_ENABLED = True
CSRF_SESSION_KEY = "somethingimpossibletoguess"
