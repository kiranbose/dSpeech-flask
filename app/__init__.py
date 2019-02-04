from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS, cross_origin

app = Flask(__name__)
socketIO = SocketIO(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

if (__name__ == "app"):
    app.run()
    socketIO.run(app)