# this file is only for database models. needless to be imported into __init__.py
from email.policy import default
import json
from flask_login import UserMixin
from sqlalchemy import null
from app import db, login_manager
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash


# about to delete. this is a temporary table for example.
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

# room table. this is supposed to be under a lobby.
# a room is equal to a game board. a room can only have 2 players. 1 host and 1 guest.
# a room can have multiple watchers, maybe set a max number.
# a room is entered as someone enter the id of the room. if the room doesn't exist, it will be created.
# a room will be deleted when no player is in the room. watchers will not affect the deletion of the room.
class Room(db.Model):
    __tablename__ = "room"
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(64), unique=True, index=True, nullable=False)   # for lobby display.
    host=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)   # TODO: use the correct token to mark who is the host
    guest=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, unique=True)   # TODO: use the correct token to mark who is the guest
    black=db.Column(db.Boolean, nullable=False, default=False)  # 0 for host, 1 for guest. TODO: play rps to decide who is black if it is the first game bettween 2 players.
    board_size=db.Column(db.Integer, nullable=False)
    gaming_status=db.Column(db.Boolean, nullable=False, default=False)  # 0 for not gaming, 1 for gaming
    host_set=db.Column(db.Text, nullable=True, default=False)   # an array of 2 numbers. 1st number is the row, 2nd number is the column. TODO: use json to store the array.
    guest_set=db.Column(db.Text, nullable=True, default=False)
    watcher_number=db.Column(db.Integer, nullable=False, default=0)


# user table. I won't put it into use until other functions fully work. This might be the last step (or maybe will never be implemented)
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
