import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    "SQLAlchemy config"
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'melon.db')
    # flask-login uses sessions which require a secret Key
    SQLALCHEMY_TRACK_MODIFICATIONS = True
