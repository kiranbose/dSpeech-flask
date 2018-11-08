from app import app, routes, transcribe, threads, auth
import os
from flask import Flask, flash, request, redirect, url_for, abort, jsonify
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson import json_util, ObjectId, Binary
from datetime import datetime
import numpy as np

# ********************************************
# Mongo DB connection functions
# ********************************************


def prepareResponse(data):
    res = {'result': data}
    return json_util.dumps(res)


def retrieve(email):
    data = routes.recordingsCollection.find()
    if routes.recordingsCollection.count() == 0:
        data = []
    return prepareResponse(data)


@app.route('/insert', methods=['POST'])
def insert():
    newCollectionId = routes.recordingsCollection.insert_one(request.json)
    newData = routes.recordingsCollection.find_one(
        {'_id': newCollectionId.inserted_id})
    return prepareResponse(newData)


def pushToDatabase(fileName, email, userPermission):
    absolutePath = os.path.abspath(os.path.join(
        app.config['UPLOAD_FOLDER'], fileName))

    # Remove Commenting of the below lines once google cloud api is up and running
    # and remove lines temp (duration and text)
    response = transcribe.transcribe_file(absolutePath)
    duration = response[0]
    text = response[1]

    # temp
    # duration = 10
    # text = 'test test'
    # temp

    # uses ffmpeg to encode and save audio files to proper wave format
    transcribe.encodeAndSaveWAVFile(absolutePath)

    monoFilePath = fileName.split('.')[0] + '__mono.wav'
    graphPath = fileName.split('.')[0] + '_plot.png'
    monoAbsolutePath = os.path.abspath(os.path.join(
        app.config['UPLOAD_FOLDER'], monoFilePath))
    dateTime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    obj = {
        'fileName': fileName,
        'stereoFilePath': absolutePath,
        'monoFilePath': monoAbsolutePath,
        'graphPath': graphPath,
        'duration_milliseconds': duration,
        'text': text,
        'wordCount': len(text.split()),
        'speed': getSpeed(duration, text),
        'timeStamp': datetime.now().strftime("%Y%m%d-%H%M%S"),
        'date': datetime.now().strftime("%d/%m/%Y"),
        'time': datetime.now().strftime("%H:%M:%S"),
        'ISOdate': datetime.strptime(dateTime, "%Y-%m-%dT%H:%M:%S.000Z"),
        'type': 'audio/wav',
        'user': routes.usersCollection.find_one({'email': email}),
        'permission': userPermission
    }
    newCollectionId = routes.recordingsCollection.insert_one(obj)
    newData = routes.recordingsCollection.find_one(
        {'_id': newCollectionId.inserted_id})
    return prepareResponse(newData)


def existInDatabase(fileName):
    data = routes.recordingsCollection.find({'fileName': fileName})
    return data and data.count() > 0

# if __name__ == 'app.auth':
#     app.secret_key = 'speechSecret'
#     app.run(debug=True)


def getSpeed(durationInMs, text):
    wordCount = len(text.split())
    return round((wordCount/(durationInMs/1000))*60)


@app.route('/metaData', methods=['GET'])
def getMetaData():
    user = auth.getLoggedInUser(request.headers['Authorization'])
    obj = {
            '$lookup':
                {
                    'from': 'powerFrequency',
                    'localField': 'stereoFilePath',
                    'foreignField': 'stereoFilePath',
                    'as': 'recordingsWithPowerData'
                }
            }
    userRecordingsWithPower = routes.recordingsCollection.aggregate([obj])
    uRecords = []
    sRecords = []
    for obj in userRecordingsWithPower:
        if (obj['user'] == user and obj['permission'] == 'guest'):
            uRecords.append(obj)
        if (obj['permission'] == 'administrator'):
            sRecords.append(obj)

    latestComparison = routes.comparisonCollection.find({'user': user})
    metaData = {
        'userRecordings': uRecords,
        'sampleRecordings': sRecords,
        'latestComparison': latestComparison
    }
    return prepareResponse(metaData)


def compareSpeechFiles(fileName1, fileName2):
    record1 = routes.recordingsCollection.find_one(
        {'stereoFilePath': fileName1})
    record2 = routes.recordingsCollection.find_one(
        {'stereoFilePath': fileName2})
    found = routes.comparisonCollection.find_one(
        {'file1': record1['_id'], 'file2': record2['_id']})
    if found:
        return found
    else:
        compareThread = threads.CompareGraphGenerator(record1, record2)
        compareThread.setName('comparing')
        compareThread.run()
        targetPath = (fileName1.split(
            '.')[0] + '+' + record2['fileName']).split('.')[0] + '.png'
        collection = routes.comparisonCollection
        newItem = collection.insert_one({
            'graphPath': targetPath,
            'file1': record1['_id'],
            'file2': record2['_id'],
            'user': record2['user'],
            'userText': record1['text'],
            'sampleText': record2['text']
        })
        # compareThread.join()
        return newItem
