from flask import Blueprint

studentmain_blueprint = Blueprint('studentmain', __name__)

from app.studmain import studroutes