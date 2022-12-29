from flask import Blueprint

gomoku = Blueprint('gomoku', __name__)

from . import routes, events