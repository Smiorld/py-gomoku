from app import create_app, socketio, db, login_manager

app = create_app(debug=True)
print(app.url_map)
if __name__ == '__main__':
    socketio.run(app)



# flask run =  import app.py or wsgi.py and (app.run() application.run() )  (socketio.run(app) 