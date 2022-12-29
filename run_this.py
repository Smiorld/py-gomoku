from app import app as application
from flask_socketio import SocketIO
socketio=SocketIO(application)


if __name__ == '__main__':
    socketio.run(application)