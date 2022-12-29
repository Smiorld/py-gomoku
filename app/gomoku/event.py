from flask import session
from flask_socketio import emit, join_room, leave_room
from .. import socketio


@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)

@socketio.on('my_event')
def handle_my_custom_event(arg1, arg2, arg3):
    print('received args: ' + arg1 + arg2 + arg3)