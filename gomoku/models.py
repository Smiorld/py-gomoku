from email.policy import default
import json
from flask_login import UserMixin
from sqlalchemy import null
from gomoku import db, login_manager
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash

class Assessment(db.Model):
    """
    Authored by Julius (Qiye Zhou)
    Modified by Rob (added time_allotted)
    """

    __tablename__ = "assessment"

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(
        db.Integer, db.ForeignKey("module.id"), nullable=False
    )  # foreign key from module table
    assessment_name = db.Column(db.Text, nullable=False)
    hand_in_date = db.Column(db.DateTime, nullable=True)
    hand_out_date = db.Column(db.DateTime, nullable=True)
    is_summative = db.Column(db.Boolean, nullable=True)
    is_draft = db.Column(db.Boolean, nullable=False, default=True)
    total_marks = db.Column(db.Integer, nullable=True, default=0)
    time_allotted = db.Column(db.Integer, nullable = True, default=0)

    # relationship()
    published_student_assessment = db.relationship(
        "PublishedStudentAssessment", backref="assessment", lazy=True
    )
    assessment2question = db.relationship(
        "Assessment2Question", backref="assessment", lazy=True
    )


class Room(db.Model):
    __tablename__ = "room"
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(64), unique=True, index=True, nullable=False)
    host=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    guest=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, unique=True)
    black=db.Column(db.Boolean, nullable=False, default=False)
    board_size=db.Column(db.Integer, nullable=False)
    gaming_status=db.Column(db.Boolean, nullable=False, default=False)
    host_set=db.Column(db.Text, nullable=True, default=False)
    guest_set=db.Column(db.Text, nullable=True, default=False)
    watcher_number=db.Column(db.Integer, nullable=False, default=0)

class User(UserMixin, db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    hashed_password = db.Column(db.String(128))


    @property
    def password(self):
        raise AttributeError("Password is not readable.")

    @password.setter
    def password(self, password):
        self.hashed_password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.hashed_password, password)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
