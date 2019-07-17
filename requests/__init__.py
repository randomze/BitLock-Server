from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
from passlib.hash import sha256_crypt
import uuid
import base64
import psycopg2

app = Flask(__name__)
api = Api(app)
connection  = psycopg2.connect(host = "localhost",
                               port = "5432",
                               user = "postgres",
                               password = "docker",
                               database = "testdb")

class UserFactory(Resource):
    def __init__(self, **kwargs):
        self.connection = kwargs['connection']
        self.cursor = self.connection.cursor()

    def post(self):
        authHeader = request.headers.get('Authorization')
        if not authHeader:
            response = jsonify({'message': 'No Authorization header provided'})
            response.headers['Content-Type'] = 'application/json'
            response.status_code = 400
            return response
        
        else:
            authType, password = authHeader.split(' ')
            if not authType == 'Basic':
                response = jsonify({'message': 'Wrong authentication type. Should be Basic'})
                response.headers['Content-Type'] = 'application/json'
                response.status_code = 400
                return response

            else:
                password = base64.b64decode(password.encode())
                #TODO: sanitize passwords cause sql injection
                
                uuid_string = str(uuid.uuid4())
                hashed_pw = sha256_crypt.encrypt(password)

                query = 'INSERT INTO users(user_id, hashed_pw) VALUES (\'{}\', \'{}\')'.format(uuid_string, hashed_pw)
                self.cursor.execute(query)
                self.connection.commit()

                response = jsonify({'message': 'User created succesfully', 'uuid': uuid_string})
                response.headers['Content-Type'] = 'application/json'
                response.status_code = 201
                return response
            
    def __del__(self):
        self.cursor.close()

class User(Resource):
    def __init__(self, **kwargs):
        self.connection = kwargs['connection']
        self.cursor = self.connection.cursor()

    def authenticateUser(self, uuid_string):
        try:
            validate = uuid.UUID(uuid_string, version = 4)
        except ValueError:
            validate = False

        validate = (validate.hex == uuid_string.replace('-', ''))

        if not validate:
            response = jsonify({'message': 'Invalid user string. Should be an UUID.'})
            response.headers['Content-Type'] = 'application/json'
            response.status_code = 400
            return response

        else:
            authHeader = request.headers.get('Authorization')
            if not authHeader:
                response = jsonify({'message': 'No Authorization header provided.'})
                response.headers['Content-Type'] = 'application/json'
                response.status_code = 400
                return response
            
            else:
                authType, password = authHeader.split(' ')
                if not authType == 'Basic':
                    response = jsonify({'message': 'Authorization type is not \'Basic.\''})
                    response.headers['Content-Type'] = 'application/json'
                    response.status_code = 400
                    return response

                else:
                    password = base64.b64decode(password.encode())

                    query = 'SELECT hashed_pw FROM users WHERE user_id = \'{}\''.format(uuid_string)
                    self.cursor.execute(query)

                    query_result = self.cursor.fetchone()
                    if not query_result:
                        response = jsonify({'message': 'No user found with the provided UUID.'})
                        response.headers['Content-Type'] = 'application/json'
                        response.status_code = 404
                        return response
                    
                    else:
                        query_result = query_result[0]
                        authorized = sha256_crypt.verify(password, query_result)

                        if not authorized:
                            response = jsonify({'message': 'Wrong password.'})
                            response.headers['Content-Type'] = 'application/json'
                            response.status_code = 401
                            return response

                        else:
                            response = jsonify({'message': 'Terrific success.'})
                            response.headers['Content-Type'] = 'application/json'
                            response.status_code = 200
                            return response

    def get(self, uuid_string):
        response = self.authenticateUser(uuid_string)        
        return response
    def __del__(self):
        self.cursor.close()

class Device(Resource):
    def __init__(self, **kwargs):
        self.connection = kwargs['connection']
        self.cursor = self.connection.cursor()
        
    def get(self, user_id):
        query = 'SELECT status FROM devices WHERE uuid_string=\'{}\''.format(user_id)
        self.cursor.execute(query)

api.add_resource(UserFactory, '/register_user', resource_class_kwargs={'connection': connection})
api.add_resource(User, '/user/<string:uuid_string>', resource_class_kwargs={'connection': connection})
api.add_resource(Device, '/user/<string:uuid_string/devices>', resource_class_kwargs={'connection': connection})