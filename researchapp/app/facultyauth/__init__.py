from flask import Blueprint

facultyauth_blueprint = Blueprint('facultyauth', __name__)

from app.facultyauth import facultyauth_routes