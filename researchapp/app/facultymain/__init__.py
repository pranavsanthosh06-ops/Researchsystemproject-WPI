from flask import Blueprint

facultymain_blueprint = Blueprint('facultymain', __name__)

from app.facultymain import facultyroutes