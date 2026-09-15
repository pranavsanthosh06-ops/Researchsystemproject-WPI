import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
# load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'research.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ROOT_PATH = basedir
    STATIC_FOLDER = os.path.join(basedir, 'app//static')
    TEMPLATE_FOLDER_STUDMAIN = os.path.join(basedir, 'app//studmain//templates')
    TEMPLATE_FOLDER_FACULTYMAIN = os.path.join(basedir, 'app//facultymain//templates')
    TEMPLATE_FOLDER_ERRORS = os.path.join(basedir, 'app//errors//templates')
    TEMPLATE_FOLDER_STUDAUTH = os.path.join(basedir, 'app//studauth//templates')
    TEMPLATE_FOLDER_FACULTYAUTH = os.path.join(basedir, 'app//facultyauth//templates')