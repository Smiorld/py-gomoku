from flask import session, request
from flask_socketio import emit, join_room, leave_room, close_room
from .. import socketio, db
from ..models import Room
import ast # for converting string to object and vice versa

def room_to_dict(room):
    return {
        'id': room.id,
        'room_name': room.room_name,
        'host': room.host,
        'guest': room.guest,
        'black' : room.black,
        'board_size': room.board_size,
        'each_drop_time': room.each_drop_time,
        'gaming_status' : room.gaming_status,
        'host_set'  : room.host_set,
        'guest_set' : room.guest_set,
        'gold_finger_set' : room.gold_finger_set,
        'watcher_number': room.watcher_number,
        'watcher_list': room.watcher_list
    }


@socketio.on('my event')
def handle_my_custom_event(arg1):
    print('received args: ' + arg1['data'] )

@socketio.on('join', namespace='/gomoku')
def on_join(data):
    sid = request.sid
    room_id = data['room_id']   # room id. TODO: make sure the value is valid in routes
    
    # on attempt to join a room, check if a room is empty
    # if not shown in the database, create a new room and set the user as the host.
    room=Room.query.filter_by(id=room_id).first()
    if room is None:
        # create a new room
        room = Room(id=room_id, host=sid )
        db.session.add(room)
        db.session.commit()
        # join the room 
        join_room(room_id, sid, namespace='/gomoku')
        # inform the client to update the room info
        emit('update room', room_to_dict(room), to=room_id, namespace='/gomoku')
    else:
        # join the room if watcher<10 (2 players + 10 watchers max per room)
        if room.watcher_number < 10 and room.host != sid and room.guest != sid:
            #check can the player be the guest
            if room.guest is None:
                # set the player as the guest player
                room.guest = sid 
                db.session.commit()
                # join the room
                join_room(room_id, sid, namespace='/gomoku')
                # inform all players in this room to update the room info
                emit('update room', room_to_dict(room), to=room_id, namespace='/gomoku')
           
            else:
                # join the room as a watcher. need to check watcher list
                watcher_list= ast.literal_eval(room.watcher_list)
                if sid not in watcher_list:
                    watcher_list.append(sid)
                    room.watcher_list = str(watcher_list)
                    room.watcher_number = room.watcher_number + 1
                else:
                    # the player is already in the watcher list
                    emit('room reject', room_to_dict(room), to=sid, namespace='/gomoku')


                db.session.commit()
                # join the room
                join_room(room_id, sid, namespace='/gomoku')
                # inform all players in this room to update the room info
                emit('update room', room_to_dict(room), to=room_id, namespace='/gomoku')
        else:
            # room is full or the player is already in the room
            # which means he can not join the room
            emit('room reject', room_to_dict(room), to=sid, namespace='/gomoku')

@socketio.on('leave', namespace='/gomoku')
def on_leave(data):
    if data['sid'] is None:
        sid = request.sid
    else:
        sid = data['sid']
    room_id = data['room_id']   # room id
    # let the sid leave the room
    leave_room(room_id, sid, namespace='/gomoku')
    # on leave , check if the room will be empty
    room=Room.query.filter_by(id=room_id).first()
    if room is not None:
        # check if room is empty. though not necessary, just in case
        if room.gaming_status == True and (room.host == sid or room.guest == sid):
            # if game is started and the player leaves is either the host or the guest, end the game
            room.gaming_status = False
            room.host_set = '[]'
            room.guest_set = '[]'
            room.black = False
        if room.host == sid:
            # if the host leaves, check if the guest is still in the room
            if room.guest is not None:
                # guest becomes the host
                room.host = room.guest
                room.guest = None
                db.session.commit()
                # inform all players in this room to update the room info
                emit('update room', room_to_dict(room), to=room_id, namespace='/gomoku')
            else:
                # no guest, delete the room
                db.session.delete(room)
                db.session.commit()
                # inform all players in this room to leave the room
                emit('leave room', room_to_dict(room), to=room_id, namespace='/gomoku')
                close_room(room_id, namespace='/gomoku')
        elif room.guest == sid:
            # if the guest leaves, set guest to None
            room.guest = None
            db.session.commit()
            # inform all in players in this room to update the room info
            emit('update room', room_to_dict(room), to=room_id, namespace='/gomoku')
        else:
            # if the watcher leaves, decrease the watcher count
            watcher_list= ast.literal_eval(room.watcher_list)
            if sid in watcher_list:
                room.watcher_number -= 1
                watcher_list.remove(sid)
                room.watcher_list = str(watcher_list)

            if room.watcher_number < 0:
                room.watcher_number = 0 # just in case. should not happen.
                print('watcher count is negative, something is wrong')
            db.session.commit()
            # inform all in players this room to update the room info
            emit('update room', room_to_dict(room), to=room_id, namespace='/gomoku')
    else:
        # room is not found, do nothing
        pass


@socketio.on('disconnect', namespace='/gomoku')
def on_disconnect():
    sid = request.sid
    # on disconnect
    rooms = Room.query.all()
    for room in rooms:
        # leave the room
        on_leave({'room_id': room.id,'sid':sid})