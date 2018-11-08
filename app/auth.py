from flask import Flask, session, request, redirect, url_for
from app import app, mongo, routes, exceptionHandler
from pymongo import MongoClient
from datetime import timedelta, datetime

import bcrypt
import os, secrets

# ********************************************
# User Authentication Protocols
# ********************************************

client = MongoClient()
db = client.speechDatabase
usersCollection = db.users
tokensCollection = db.tokens
appName = Flask(__name__)
appName.secret_key = os.urandom(24)

@app.route('/login', methods=['POST'])
def login():
    login_user = usersCollection.find_one({'email' : request.json['email']})
    if login_user:
        if bcrypt.checkpw(request.json['password'].encode('utf-8'), login_user['password']):
            token = secrets.token_hex(20)
            tokensCollection.delete_one({ 'email' : request.json['email']})
            tokensCollection.insert({
                'token': token,
                'email': request.json['email'],
                'expiry': (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            })
            response = { 'email': login_user['email'], 'firstName': login_user['firstName'], 'token': token, 'permission': login_user['permission'] }
            return mongo.prepareResponse(response)
    raise exceptionHandler.InvalidUsage('Invalid email/password combination', status_code=420)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        existing_user = usersCollection.find_one({'email' : request.json['email']})
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.json['password'].encode('utf-8'), bcrypt.gensalt())
            usersCollection.insert({
                'firstName' : request.json['firstName'], 
                'lastNname' : request.json['lastName'], 
                'email' : request.json['email'], 
                'empId' : request.json['empId'], 
                'password' : hashpass,
                'industry' : request.json['industry'], 
                'serviceLine' : request.json['serviceLine'], 
                'serviceArea' : request.json['serviceArea'], 
                'designation' : request.json['designation'], 
                'location' : request.json['location'], 
                'mobileNo' : request.json['mobileNo'],
                'permission': 'guest'
                })
            newUser = usersCollection.find({'email' : request.json['email']}, {'password': 0})
            return mongo.prepareResponse(newUser)
        else:
            raise exceptionHandler.InvalidUsage('User already exists', status_code=420)


@app.route('/getAllUsers', methods=['GET'])
def users():
    if request.method == 'GET':
        existing_users = usersCollection.find({'permission' : 'guest'}, {'password': 0})
        if existing_users:
            return mongo.prepareResponse(existing_users)
        else:
            raise exceptionHandler.InvalidUsage('No Users', status_code=420)


# if __name__ == 'app.auth':
#     app.secret_key = 'speechSecret'
#     app.run(debug=True)

def isUserLoggedIn(token):
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    ceil = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    oldValue = { "expiry": { "$lte": now } }
    newvalue = { "$set": { "expiry": ceil } }
    tokensCollection.delete_many(oldValue)
    loggedInUser = tokensCollection.find_one({'token': token})
    if loggedInUser is not None:
        tokensCollection.update_one(oldValue, newvalue)
        return True
    return None


def getLoggedInUser(token):
    loggedInUser = tokensCollection.find_one({'token': token})
    if loggedInUser is not None:
        user = usersCollection.find_one({"email": loggedInUser['email']})
        return user
    return None
    