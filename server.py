#!/usr/bin/env python3
from auth import user, validation
import base64
from flask import Flask, request, g, jsonify, redirect
import json
import psycopg2

app = Flask(__name__)

def connect_to_database():
    if 'connection' not in g:
        g.connection = psycopg2.connect(database = 'testdb',
                                                     host = 'localhost',
                                                     port = '5432',
                                                     user = 'postgres',
                                                     password = 'docker')

    return g.connection    

@app.teardown_appcontext
def cleanup_connection(exception):
    connection = g.pop('connection', None)

    if connection is not None:
        connection.commit()
        connection.close()

'''@app.before_request
def enforceHttps():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code = code)'''

@app.route('/auth/registration', methods = ['POST'])
def new_user():
    print(request.headers)
    data = request.json

    reply = user.loginOrRegistration(connect_to_database().cursor(), data['email'], data['password'], 'yau', 'registration')

    return jsonify({'status': 'success', 'token': reply[0], 'unique': reply[1]})

@app.route('/auth/token', methods = ['POST'])
def get_user_token():
    print(request.headers)
    print(request.json)
    data = request.json

    reply = user.loginOrRegistration(connect_to_database().cursor(), data['email'], data['password'], 'yau', 'login')

    if reply:
        return jsonify({'status': 'success', 'token': reply[0], 'unique': reply[1]})
    else:
        return jsonify({'status': 'failed', 'message': 'bad logins'})

@app.route('/devices/<string:unique_id>', methods = ['POST'])
def add_device(unique_id):
    data = request.json

    token = request.headers['Authorization']

    valid, message = validation.authenticate(connect_to_database().cursor(), token, 'yau')
    
    if not valid:
        return jsonify({'status': 'failed', 'message': message})
    else:
        if not message == unique_id:
            return jsonify({'status': 'failed', 'message': 'token not for this user'})
        else:
            query = 'INSERT INTO devices(owner, identifier, master_id) VALUES (\'{}\', \'{}\', \'{}\');'.format(unique_id, data['identifier'], data['master_id'])
            connect_to_database().cursor().execute(query)
            return jsonify({'status': 'success', 'message': 'device added sucessfully'})

@app.route('/devices/<string:unique_id>/<string:device>', methods = ['DELETE'])
def remove_device():
    pass

@app.route('/devices/<string:unique_id>', methods = ['GET'])
def get_devices(unique_id):
    token = request.headers['Authorization']

    valid, message = validation.authenticate(connect_to_database().cursor(), token, 'yau')

    if not valid:
        return jsonify({'status': 'failed', 'message': message})
    else:
        if not message == unique_id:
            return jsonify({'status': 'failed', 'message': 'token not for this user'})
        else:
            query = 'SELECT identifier FROM devices WHERE owner=\'{}\';'.format(unique_id)
            cursor = connect_to_database().cursor()
            cursor.execute(query)
            devices = [x[0] for x in cursor.fetchall()]
            return jsonify({'status': 'success', 'devices': devices})

@app.route('/devices/waiting/<string:device_unique_id>', methods = ['GET'])
def get_device_queue(device_unique_id):
    pass

@app.route('/devices/<string:unique_id>/<string:device>', methods = ['PUT'])
def unlock_device():
    pass


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)