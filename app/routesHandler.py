from app import app, auth, mongoConnector, retrieveData, exceptionHandler, uploader
import os
from flask import Flask, flash, request, redirect, url_for, abort, jsonify, session, g
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson import json_util, ObjectId, Binary
from datetime import datetime, timedelta
import bcrypt
import numpy as np
import soundfile
from flask_cors import CORS, cross_origin
# from flask_socketio import SocketIO
# socketio = SocketIO(app)

# if (__name__ == "app.routes"):
#     socketio.run(app)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

client = MongoClient()
folderName = 'uploads'
UPLOAD_FOLDER = './'
ALLOWED_EXTENSIONS = set(['wav'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = client.speechDatabase
recordingsCollection = db.recordings
comparisonCollection = db.comparisons
usersCollection = db.users

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', defaults={'path': ''})
@cross_origin()
def catch_all(path):
    return 'You want path: %s' % path

@app.before_request
def before_request():
    if request.method != 'OPTIONS':
        if request.endpoint == 'login' or request.endpoint == 'register':
            admin = usersCollection.find_one({ 'email': 'admin' })
            if admin is None :
                usersCollection.insert_one(adminObj)
        elif 'Authorization' not in request.headers:
            raise exceptionHandler.InvalidUsage('Un Authorized User', status_code=420)
        if 'Authorization' in request.headers and auth.isUserLoggedIn(request.headers['Authorization']) is None:
            raise exceptionHandler.InvalidUsage('Session Timed Out', status_code=420)
    else:
        return ''

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        #  file = request.files['file']
        #     if file and allowed_file(file.filename):
        #         filename = secure_filename(file.filename)
        #         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        #         ## snippet to read code below
        #         file.stream.seek(0) # seek to the beginning of file
        #         myfile = file.file # will point to tempfile itself
        #         dataframe = pd.read_csv(myfile)
        #         ## end snippet
        user = auth.getLoggedInUser(request.headers['Authorization'])
        # check if the post request has the file part
        file = request.files.get('file')
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No file part')
            return exceptionHandler.InvalidUsage('Invalid Recording', status_code=420)
        if file and allowed_file(file.filename) and not mongoConnector.existInDatabase(file.filename):
            filename = uploader._safe_filename(file.filename)
            file.save('./' + filename)
            response = mongoConnector.pushToDatabase(filename, user['email'], user['permission'])
            return mongoConnector.prepareResponse(response)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=upload>
    </form>
    '''

adminObj = {
    'firstName' : 'admin', 
    'lastNname' : 'admin', 
    'email' : 'admin',
    'empId' : '0000',
    'password' : bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt()),
    'industry' : 'admin', 
    'serviceLine' : 'admin', 
    'serviceArea' : 'admin', 
    'designation' : 'admin', 
    'location' : 'admin', 
    'mobileNo' : 'admin',
    'permission': 'administrator'
}

@app.route('/getFileData', methods=['GET', 'POST'])
def getFileData():
    fileName1 = request.json['fileName1']
    fileName2 = request.json['fileName2']
    compareObj = mongoConnector.compareSpeechFiles(fileName1, fileName2)
    return json_util.dumps({
        'plotUrl': compareObj['plotUrl'],
        'fileName': compareObj['fileName'],
        'userText': compareObj['userText'],
        'sampleText': compareObj['sampleText'],
        })

@app.route('/getUserAudioFiles', methods=['GET', 'POST'])
def getUserAudioFiles():
    user = auth.getLoggedInUser(request.headers['Authorization'])
    print(user['email'])
    return mongoConnector.retrieve(user['email'])

@app.route('/getDemoUserAudioFiles', methods=['GET', 'POST'])
def getDemoUserAudioFiles():
    return retrieveData.retrieveDemoRecordings()

@app.route('/getMyUserAudioFiles', methods=['GET', 'POST'])
def getMyUserAudioFiles():
    user = auth.getLoggedInUser(request.headers['Authorization'])
    return retrieveData.retrieveMyRecordings(user['email'])


# @socketio.on('graph')
# def handle_graph(json):
#     print('received json: ' + str(json))


# @socketio.on('clientConnected')
# def handle_connection(json):
#     print('received json: ' + str(json))

# @socketio.on('connect')
# def test_connect():
#     print('Client Connected')

# @socketio.on('disconnect')
# def test_disconnect():
#     print('Client disconnected')
