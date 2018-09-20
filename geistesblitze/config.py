from os.path import abspath, dirname, join

basedir = abspath(dirname(__file__))


class Config(object):
    SECRET_KEY = 'hard to guess string'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////%s' % join(basedir, 'geistesblitze.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
