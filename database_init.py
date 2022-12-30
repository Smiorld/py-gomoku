from sqlalchemy import true
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.models import (
    User,
    Room
    
)

app = Flask(__name__)
app.debug = False


# suppress SQLAlchemy warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['SECRET_KEY'] = 'lalaowow'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "/app/data.db")

db = SQLAlchemy(app)

db.drop_all()
db.create_all()
db.session.commit()