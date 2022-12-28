import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_ckeditor import CKEditor

app = Flask(__name__)
# add ckeditor for rich text fields
ckeditor = CKEditor(app)

# suppress SQLAlchemy warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data.db")
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)

from gomoku import routes