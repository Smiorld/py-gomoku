import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_socketio import SocketIO

socketio = SocketIO()
db= SQLAlchemy()
login_manager = LoginManager()

def create_app(make_db=False,debug=False) -> Flask:


    app = Flask(__name__)
    app.debug = debug

    # add ckeditor for rich text fields
    ckeditor = CKEditor(app)

    # suppress SQLAlchemy warning
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config['SECRET_KEY'] = 'lalaowow'

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data.db")

    from .gomoku import gomoku as gomoku_blueprint
    app.register_blueprint(gomoku_blueprint)

    db.init_app(app)
    if make_db:
        with app.app_context():
            from . import models
            db.drop_all()
            db.create_all()
            db.session.commit()


    socketio.init_app(app)
    login_manager.init_app(app)
    return app

from . import models