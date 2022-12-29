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

@gomoku.route("/room/<int:room_number>/<int:player_number>", methods=["GET", "POST"])
def room(room_number, player_number):

    return render_template("board.html", board_size=13, room_number=room_number, player_number=player_number)

@gomoku.route("/drop_a_piece/<int:room_number>/<int:player_number>/<int:row>/<int:column>", methods=["POST"])
def drop_a_piece(room_number, player_number, row, column):

    return render_template("board.html", board_size=13, room_number=room_number, player_number=player_number)

@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)

@socketio.on('my_event')
def handle_my_custom_event(arg1, arg2, arg3):
    print('received args: ' + arg1 + arg2 + arg3)