from flask import Blueprint

studentauth_blueprint = Blueprint('studentauth', __name__)

from app.studauth import studauth_routes