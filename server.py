#!/usr/bin/env python3
from auth import user, validation
import base64
from flask import Flask, request, g, jsonify, redirect
import json
import psycopg2
import uuid
import os

DATABASE_URL = os.environ['DATABASE_URL']

app = Flask(__name__)

#Configure the database connection and make it available on request
def connect_to_database():
    if 'connection' not in g:
        g.connection = psycopg2.connect(DATABASE_URL, sslmode='require')

    return g.connection    

#After handling each request commit the changes made to the database and close the connection
@app.teardown_appcontext
def cleanup_connection(exception):
    connection = g.pop('connection', None)

    if connection is not None:
        connection.commit()
        connection.close()

#Make sure the connection is running on HTTPS to guarantee security
@app.before_request
def enforceHttps():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code = code)

#The route statements indicate what is to be done when a request reaches the determined endpoint with the specified methods

#Register a new user
@app.route('/auth/registration', methods = ['POST'])
def new_user():
    #read the json request data into a dictionary
    data = request.json

    #forward the credentials to the authentication service
    reply = user.loginOrRegistration(connect_to_database().cursor(), data['email'], data['password'], 'some-secret', 'registration')

    return jsonify({'status': 'success', 'token': reply[0], 'unique': reply[1]})

#Give an acess token for an already registered user
@app.route('/auth/token', methods = ['POST'])
def get_user_token():
    #same as above, read the data and forward it to the auth service
    data = request.json
    reply = user.loginOrRegistration(connect_to_database().cursor(), data['email'], data['password'], 'some-secret', 'login')

    #if credentials are valid return the token otherwise return failure
    if reply:
        return jsonify({'status': 'success', 'token': reply[0], 'unique': reply[1]})
    else:
        return jsonify({'status': 'failed', 'message': 'bad logins'})

#Register new device with user
@app.route('/devices/<string:unique_id>', methods = ['POST'])
def add_device(unique_id):
    #get request data
    data = request.json

    #validate token and authenticate user
    token = request.headers['Authorization']
    valid, message = validation.authenticate(connect_to_database().cursor(), unique_id, token, 'some-secret')

    #depending on the token validation and user authentication, register, or don't, the new device and reply accordingly
    if not valid:
        return jsonify({'status': 'failed', 'message': message})
    else:
        query = 'INSERT INTO devices(owner, identifier, master_id) VALUES (\'{}\', \'{}\', \'{}\');'.format(unique_id, data['identifier'], data['master_id'])
        connect_to_database().cursor().execute(query)
        return jsonify({'status': 'success', 'message': 'device added sucessfully'})

#Register a new master device with user
@app.route('/devices/<string:unique_id>/master', methods = ['POST'])
def add_master(unique_id):
    #same as above
    token = request.headers['Authorization']
    valid, message = validation.authenticate(connect_to_database().cursor(), unique_id, token, 'some-secret')

    if not valid:
        return jsonify({'status': 'failed', 'message': message})
    else:
        #generate an id for the master
        unique_device_id = str(uuid.uuid4())

        #insert it into the database
        query = 'INSERT INTO master_lookup(master_id, owner) VALUES (\'{}\', \'{}\');'.format(unique_device_id, unique_id)
        cursor = connect_to_database().cursor()
        cursor.execute(query)

        #create a row for its message queue on the database
        query = 'INSERT INTO masters_messages(master_id, message) VALUES (\'{}\', \'\');'.format(unique_device_id)
        cursor.execute(query)
        cursor.close()

        #return the id to the user
        return jsonify({'status': 'success', 'master_id': unique_device_id, 'message': 'master added sucessfully'})

'''@app.route('/devices/<string:unique_id>/<string:device>', methods = ['DELETE'])
def remove_device():
    pass'''

#Get users devices
@app.route('/devices/<string:unique_id>', methods = ['GET'])
def get_devices(unique_id):
    #validate and authenticate
    token = request.headers['Authorization']
    valid, message = validation.authenticate(connect_to_database().cursor(), unique_id, token, 'some-secret')

    #respond accordingly
    if not valid:
        return jsonify({'status': 'failed', 'message': message})
    else:
        #read the device list from the database
        query = 'SELECT identifier FROM devices WHERE owner=\'{}\';'.format(unique_id)
        cursor = connect_to_database().cursor()
        cursor.execute(query)
        devices = [x[0] for x in cursor.fetchall()]
        return jsonify({'status': 'success', 'devices': devices})

#Master device message queue
@app.route('/devices/waiting/<string:master_id>', methods = ['GET'])
def get_device_queue(master_id):
    cursor = connect_to_database().cursor()

    #Check for messages for the device
    query = 'SELECT message FROM masters_messages WHERE master_id=\'{}\';'.format(master_id)
    cursor.execute(query)
    result = cursor.fetchone()

    #If there aren't any, return 'DO NOTHING', otherwise forward it the message
    if not result or not result[0]:
        cursor.close()
        return 'DO NOTHING'
    else:
        query = 'UPDATE masters_messages SET message=NULL WHERE master_id=\'{}\''.format(master_id)
        cursor.execute(query)
        cursor.close()
        return result[0]

#Unlock device
@app.route('/devices/<string:unique_id>/<string:identifier>', methods = ['PUT'])
def unlock_device(unique_id, identifier):
    #validate and authenticate
    token = request.headers['Authorization']
    valid, message = validation.authenticate(connect_to_database().cursor(), unique_id, token, 'some-secret')

    if not valid:
        return jsonify({'status': 'failed', 'message': message})
    else:
        #Lookup which master device is assigned to the requested device
        query = 'SELECT master_id FROM devices WHERE owner=\'{}\' AND identifier=\'{}\';'.format(unique_id, identifier)
        cursor = connect_to_database().cursor()
        cursor.execute(query)
        result = cursor.fetchone()

        #If there isn't one respond with failure, otherwise let the master know to open the request device
        if not result:
            cursor.close()
            return jsonify({'status': 'failed', 'message': 'No such device for the given owner'})
        else:
            message = 'OPEN {}'.format(identifier)
            
            #Push the message to the masters queue
            query = 'UPDATE masters_messages SET message=\'{}\' WHERE master_id=\'{}\';'.format(message, result[0])
            cursor.execute(query)
            cursor.close()
            return jsonify({'status': 'success', 'message': 'Door opening', 'result': result[0]})
