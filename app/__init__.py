from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketIO = SocketIO(app)

from app import routes

if (__name__ == "app"):
    app.run()
    socketIO.run(app)