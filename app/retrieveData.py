from app import app, routesHandler, transcribe
import os
from flask import Flask, flash, request, redirect, url_for, abort, jsonify
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson import json_util, ObjectId, Binary
from datetime import datetime

# ********************************************
# Mongo DB connection functions
# ********************************************

def prepareResponse(data):
    res = { 'result': data }
    return json_util.dumps(res)

def retrieveMyRecordings(email):
    data = routesHandler.recordingsCollection.find({"email": email})
    if routesHandler.recordingsCollection.count() == 0:
        data = "no data"
    return prepareResponse(data)

def retrieveDemoRecordings():
    data = routesHandler.recordingsCollection.find({"user": "systemuser"})
    if routesHandler.recordingsCollection.count() == 0:
        data = "no data"
    return prepareResponse(data)
