from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager
from flask_moment import Moment
from flask_mail import Mail
from os import environ as env
from dotenv import find_dotenv, load_dotenv
from authlib.integrations.flask_client import OAuth


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'studentmain.main'
moment = Moment()
mail = Mail()
oauth = OAuth()

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.static_folder = config_class.STATIC_FOLDER
    #app.template_folder = config_class.TEMPLATE_FOLDER_MAIN

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'codeclique3@gmail.com'
    app.config['MAIL_PASSWORD'] = 'gdvk tvfv oowa hqna'
    app.config['MAIL_DEFAULT_SENDER'] = 'codeclique3@gmail.com'

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    moment.init_app(app)
    mail.init_app(app)

    oauth.init_app(app)
    oauth.register(
        "auth0",
        client_id = env.get("AUTH0_CLIENT_ID"),
        client_secret = env.get("AUTH0_CLIENT_SECRET"),
        client_kwargs = {
            "scope" : "openid profile email",
        },
        server_metadata_url = f"https://{env.get('AUTH0_DOMAIN')}/.well-known/openid-configuration"
    )

    #register blueprints
    from app.studmain import studentmain_blueprint as smain
    smain.template_folder = Config.TEMPLATE_FOLDER_STUDMAIN
    app.register_blueprint(smain)

    from app.studauth import studentauth_blueprint as sauth
    sauth.template_folder = Config.TEMPLATE_FOLDER_STUDAUTH
    app.register_blueprint(sauth)

    from app.facultymain import facultymain_blueprint as fmain
    fmain.template_folder = Config.TEMPLATE_FOLDER_FACULTYMAIN
    app.register_blueprint(fmain)

    from app.facultyauth import facultyauth_blueprint as fauth
    fauth.template_folder = Config.TEMPLATE_FOLDER_FACULTYAUTH
    app.register_blueprint(fauth)

    from app.errors import error_blueprint as errors
    errors.template_folder = Config.TEMPLATE_FOLDER_ERRORS
    app.register_blueprint(errors)

    return app
