import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SECURE = False
    PHOTOS = '/static/photos'
    UPLOAD_FOLDER = os.path.join(basedir, 'app') + PHOTOS
    ALLOWED_EXTENSIONS = set(['jpg', 'png', 'gif', 'jpeg'])
    REMINDERS_PER_PAGE = 30