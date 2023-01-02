import eventlet
eventlet.monkey_patch()
from flask import session, request, current_app, copy_current_request_context
from flask_socketio import emit, send, join_room, leave_room, close_room
from .text import text
from .. import socketio, db, app
from ..models import Room
import ast # for converting string to object and vice versa
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from pytz import utc
from datetime import datetime, timedelta

language='chinese' # default language is chinese for now 
# TODO: add language selection

# set the scheduler
executors = {
    'default': ThreadPoolExecutor(100),
    'processpool': ProcessPoolExecutor(5)
}
scheduler = BackgroundScheduler(executors=executors, timezone=utc)
scheduler.start()

def room_to_dict(room):
    return {
        'id': room.id,
        'room_name': room.room_name,
        'host': room.host,
        'guest': room.guest,
        'black' : room.black,
        'board_size': room.board_size,
        'each_turn_time': room.each_turn_time,
        'gaming_status' : room.gaming_status,
        'turn' : room.turn,
        'host_set'  : room.host_set,
        'guest_set' : room.guest_set,
        'gold_finger_set' : room.gold_finger_set,
        'watcher_number': room.watcher_number,
        'watcher_list': room.watcher_list
    }

def turn_over_time(room_id): # one player loses because of time out
    with app.app_context():
        room=Room.query.filter_by(id=room_id).first()
        if room is not None:
            if room.turn:
                # guest loses because of time out
                game_over(room_id, room, 1)
            else:
                # host loses because of time out
                game_over(room_id, room, 2)

def time_out_date(seconds):
    return ( datetime.utcnow() + timedelta(seconds=seconds) )

def add_job_timer(room_id, room):
    scheduler.add_job(turn_over_time, 'date', run_date=time_out_date(room.each_turn_time), args=[room_id], id=str(room_id))
    print(scheduler.get_jobs())

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
            # if game is started and the player left is either the host or the guest, end the game
            room.gaming_status = False
            room.turn = False
            room.host_set = '[]'
            room.guest_set = '[]'
            room.black = False
            db.session.commit()

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
                emit('update room', room_to_dict(room), to=room_id, namespace='/gomoku')
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

@socketio.on('start game', namespace='/gomoku')
def on_start_game(data):
    room_id=data['room_id']
    room = Room.query.filter_by(id=room_id).first()
    if room is not None:
        if room.host == request.sid and room.guest is not None and room.gaming_status == False:
            # only host can start the game
            room.host_set = '[]'
            room.guest_set = '[]'
            room.gaming_status = True
            db.session.commit()
            # inform all players in this room to update the room info
            emit('game start', room_to_dict(room), to=room_id, namespace='/gomoku')
            add_job_timer(room_id, room)

@socketio.on('place a piece', namespace='/gomoku')
def on_place_a_piece(data):
    # validate whether its the player's turn
    room_id=data['room_id']
    room = Room.query.filter_by(id=room_id).first()
    if room is not None:
        if room.gaming_status == True and (room.host == request.sid or room.guest == request.sid):
            if ( (data['role']=='guest')==(room.turn)   ):
                # if it's the player's turn
                # validate the piece
                host_set= ast.literal_eval(room.host_set)
                guest_set= ast.literal_eval(room.guest_set)
                if  data['row']<0 or data['row']>=data['board_size'] or \
                    data['col']<0 or data['col']>=data['board_size'] or \
                    [data['row'],data['col']] in host_set or            \
                    [data['row'],data['col']] in guest_set:

                    # if the piece is already placed or out of range (TODO:error), do nothing
                    pass
                else:
                    # place the piece
                    if data['role']=='host':
                        host_set.append([data['row'],data['col']])
                        room.host_set = str(host_set)
                    else:
                        guest_set.append([data['row'],data['col']])
                        room.guest_set = str(guest_set)
                    # change the turn
                    room.turn = not room.turn
                    
                    db.session.commit()


                    # inform all players in this room to update the room info
                    emit('update room', room_to_dict(room), to=room_id, namespace='/gomoku')

                    # check if the game is over
                    is_game_over = check_game_over(room)
                    if is_game_over:
                        # TODO: if game is over, reset the room info
                        room.gaming_status = False
                        room.host_set = '[]'
                        room.guest_set = '[]'
                        room.black = not room.black
                        room.turn = room.black
                        db.session.commit()
                        if is_game_over==1:
                            # host win
                            send(text[language]['host wins'], to=room_id, namespace='/gomoku')

                            #end the timer
                            scheduler.remove_job(str(room_id))


                            # inform all players in this room to update the room info
                            emit('update room', room_to_dict(room), to=room_id, namespace='/gomoku')

                        elif is_game_over==2:
                            # guest win
                            send(text[language]['guest wins'], to=room_id, namespace='/gomoku')

                            #end the timer
                            scheduler.remove_job(str(room_id))

                            # inform all players in this room to update the room info
                            emit('update room', room_to_dict(room), to=room_id, namespace='/gomoku')

                        else:
                            # draw
                            send(text[language]['draw'], to=room_id, namespace='/gomoku')

                            #end the timer
                            scheduler.remove_job(str(room_id))

                            # inform all players in this room to update the room info
                            emit('update room', room_to_dict(room), to=room_id, namespace='/gomoku')
                    else:
                        scheduler.reschedule_job(str(room_id), run_date=time_out_date(room.each_turn_time) ) # refresh the timer
                    
                    

def check_game_over(room): # 0 for not over, 1 for host win, 2 for guest win, 3 for draw
    host_set = ast.literal_eval(room.host_set)
    guest_set = ast.literal_eval(room.guest_set)
    # check host winning or not
    if check_win(host_set):
        return 1
    elif check_win(guest_set):
        return 2
    elif len(host_set)+len(guest_set) == room.board_size*room.board_size:
        return 3
    else:
        return 0

def check_win(piece_set):
    # check if the piece set is a winning set
    for piece in piece_set:
        # check 4 directions: left-down, down, right-down, right
        if check_direction(piece_set, piece, [1,-1]) or \
            check_direction(piece_set, piece, [1,0]) or \
            check_direction(piece_set, piece, [1,1]) or \
            check_direction(piece_set, piece, [0,1]):
            return True
    return False

def check_direction(piece_set, piece, direction):
    # check if the piece is in a winning set in a direction
    count = 0
    for i in range(5):
        if [piece[0]+i*direction[0], piece[1]+i*direction[1]] in piece_set:
            count += 1
        else:
            break
    for i in range(1,5):
        if [piece[0]-i*direction[0], piece[1]-i*direction[1]] in piece_set:
            count += 1
        else:
            break
    if count >= 5:
        return True
    else:
        return False


def game_over(room_id, room, is_game_over): # is_game_over: 0 for not over, 1 for host win, 2 for guest win, 3 for draw
        if is_game_over:
            # TODO: if game is over, reset the room info
            room.gaming_status = False
            room.host_set = '[]'
            room.guest_set = '[]'
            room.black = not room.black
            room.turn = room.black
            db.session.commit()
            if is_game_over==1:
                # host win
                send(text[language]['host wins'], to=room_id, namespace='/gomoku')

                # inform all players in this room to update the room info
                emit('update room', room_to_dict(room), to=room_id, namespace='/gomoku')

            elif is_game_over==2:
                # guest win
                send(text[language]['guest wins'], to=room_id, namespace='/gomoku')

                # inform all players in this room to update the room info
                emit('update room', room_to_dict(room), to=room_id, namespace='/gomoku')

            else:
                # draw
                send(text[language]['draw'], to=room_id, namespace='/gomoku')

                # inform all players in this room to update the room info
                emit('update room', room_to_dict(room), to=room_id, namespace='/gomoku')
        else:
            # inform all players in this room to update the room info
            emit('update room', room_to_dict(room), to=room_id, namespace='/gomoku')
            scheduler.reschedule_job(str(room_id), run_date=time_out_date(room.each_turn_time) ) # refresh the timer

@socketio.on('disconnect', namespace='/gomoku')
def on_disconnect():
    sid = request.sid
    # on disconnect
    rooms = Room.query.all()
    for room in rooms:
        # leave the room
        on_leave({'room_id': room.id,'sid':sid})