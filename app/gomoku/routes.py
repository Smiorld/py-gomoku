from flask import (
    Flask,
    render_template,
    url_for,
    redirect,
    request,
    flash,
    jsonify,
    make_response,
)
from . import gomoku
from .text import text
from .. import db
from ..models import User, Room

language='chinese' # default language is chinese for now 
# TODO: add language selection

@gomoku.route("/room/<int:room_id>", methods=["GET", "POST"])
def room(room_id):
    if isinstance(room_id,int) and room_id<100 and room_id>0:
        room = Room.query.filter_by(id=room_id).first()
        if room is None:
            #TODO: config the room using the configs stored in the User database.
            return render_template("board.html", board_size=15, room_id=room_id, text=text[language])
        else:
            return render_template("board.html", board_size=room.board_size, room_id=room_id, text=text[language])
    else:
        return text[language]['invalid_room_id']
        # TODO: better error page with redirect to the home page
    

@gomoku.route("/drop_a_piece/<int:room_number>/<int:player_number>/<int:row>/<int:column>", methods=["POST"])
def drop_a_piece(room_number, player_number, row, column):

    return render_template("board.html", board_size=13, room_number=room_number, player_number=player_number)
