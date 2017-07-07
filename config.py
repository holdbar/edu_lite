import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.urandom(24)
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'edu.db')
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)

class ProductionConfig(Config):
    DEBUG = False


class DevelopConfig(Config):
    DEBUG = True
    ASSETS_DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
