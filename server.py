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

def connect_to_database():
    if 'connection' not in g:
        g.connection = psycopg2.connect(DATABASE_URL, sslmode='require')

    return g.connection    

@app.teardown_appcontext
def cleanup_connection(exception):
    connection = g.pop('connection', None)

    if connection is not None:
        connection.commit()
        connection.close()

@app.before_request
def enforceHttps():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code = code)

@app.route('/auth/registration', methods = ['POST'])
def new_user():
    print(request.headers)
    data = request.json

    reply = user.loginOrRegistration(connect_to_database().cursor(), data['email'], data['password'], 'some-secret', 'registration')

    return jsonify({'status': 'success', 'token': reply[0], 'unique': reply[1]})

@app.route('/auth/token', methods = ['POST'])
def get_user_token():
    print(request.headers)
    print(request.json)
    data = request.json

    reply = user.loginOrRegistration(connect_to_database().cursor(), data['email'], data['password'], 'some-secret', 'login')

    if reply:
        return jsonify({'status': 'success', 'token': reply[0], 'unique': reply[1]})
    else:
        return jsonify({'status': 'failed', 'message': 'bad logins'})

@app.route('/devices/<string:unique_id>', methods = ['POST'])
def add_device(unique_id):
    data = request.json

    token = request.headers['Authorization']
    valid, message = validation.authenticate(connect_to_database().cursor(), unique_id, token, 'some-secret')

    if not valid:
        return jsonify({'status': 'failed', 'message': message})
    else:
        query = 'INSERT INTO devices(owner, identifier, master_id) VALUES (\'{}\', \'{}\', \'{}\');'.format(unique_id, data['identifier'], data['master_id'])
        connect_to_database().cursor().execute(query)
        return jsonify({'status': 'success', 'message': 'device added sucessfully'})

@app.route('/devices/<string:unique_id>/master', methods = ['POST'])
def add_master(unique_id):
    token = request.headers['Authorization']

    valid, message = validation.authenticate(connect_to_database().cursor(), unique_id, token, 'some-secret')

    if not valid:
        return jsonify({'status': 'failed', 'message': message})
    else:
        unique_device_id = str(uuid.uuid4())

        query = 'INSERT INTO master_lookup(master_id, owner) VALUES (\'{}\', \'{}\');'.format(unique_device_id, unique_id)
        cursor = connect_to_database().cursor()
        cursor.execute(query)
        cursor.close()

        return jsonify({'status': 'success', 'master_id': unique_device_id, 'message': 'master added sucessfully'})

'''@app.route('/devices/<string:unique_id>/<string:device>', methods = ['DELETE'])
def remove_device():
    pass'''

@app.route('/devices/<string:unique_id>', methods = ['GET'])
def get_devices(unique_id):
    token = request.headers['Authorization']

    valid, message = validation.authenticate(connect_to_database().cursor(), unique_id, token, 'some-secret')

    if not valid:
        return jsonify({'status': 'failed', 'message': message})
    else:
        query = 'SELECT identifier FROM devices WHERE owner=\'{}\';'.format(unique_id)
        cursor = connect_to_database().cursor()
        cursor.execute(query)
        devices = [x[0] for x in cursor.fetchall()]
        return jsonify({'status': 'success', 'devices': devices})

@app.route('/devices/waiting/<string:master_id>', methods = ['GET'])
def get_device_queue(master_id):
    cursor = connect_to_database().cursor()

    query = 'SELECT message FROM masters_messages WHERE master_id=\'{}\';'.format(master_id)
    cursor.execute(query)
    result = cursor.fetchone()

    if not result:
        cursor.close()
        return ('DO NOTHING', 200, 'text/plain')
    else:
        query = 'UPDATE masters_messages SET message=NULL WHERE master_id=\'{}\''.format(master_id)
        cursor.execute(query)
        cursor.close()
        return (result[0], 200, 'text/plain')

@app.route('/devices/<string:unique_id>/<string:identifier>', methods = ['PUT'])
def unlock_device(unique_id, identifier):
    token = request.headers['Authorization']

    valid, message = validation.authenticate(connect_to_database().cursor(), unique_id, token, 'some-secret')

    if not valid:
        return jsonify({'status': 'failed', 'message': message})
    else:
        query = 'SELECT master_id FROM devices WHERE owner=\'{}\', identifier=\'{}\';'.format(unique_id, identifier)
        cursor = connect_to_database().cursor()
        cursor.execute(query)
        result = cursor.fetchone()

        if not result:
            cursor.close()
            return jsonify({'status': 'failed', 'message': 'No such device for the given owner'})
        else:
            message = 'OPEN {}'.format(identifier)
            
            query = 'UPDATE masters_messages SET message=\'{}\' WHERE master_id=\'{}\';'.format(message, result)
            cursor.execute(query)
            cursor.close()
            return jsonify({'status': 'success', 'message': 'Door opening'})
