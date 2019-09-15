from datetime import datetime
from auth import jwt
import json
import psycopg2

def authenticate(cursor, unique_id, token, secret):
    valid, data = jwt.verifyJWT(token, secret)

    if valid:
        #fetch token from database
        query = 'SELECT token FROM tokens WHERE owner_unique=\'{}\';'.format(unique_id)
        cursor.execute(query)
        query_results = cursor.fetchone()
        cursor.close()
        #check if there is such a user
        if not query_results:
            return (False, 'owner_no_token')
        else:
            dbtoken = query_results[0]

            #check if the token for the user is the one in the database
            if not dbtoken == token:
                return (False, 'token_different_owner')
            else:
                return (True, data['owner_unique'])
    else:
        cursor.close()
        return (False, 'token_bad_signature')

def generateToken(cursor, unique_id, secret):
    header = {}
    header['alg'] = 'HS256'
    header['typ'] = 'JWT'

    data = {}
    data['owner_unique'] = unique_id

    #make the token
    token = jwt.makeJWT(json.dumps(header), json.dumps(data), secret)

    #check if there is already any token for the user
    query = 'SELECT token FROM tokens WHERE owner_unique=\'{}\';'.format(unique_id)
    cursor.execute(query)

    result = cursor.fetchone()

    #if there isnt insert it into the database otherwise replace it
    if not result:
        query = 'INSERT INTO tokens (owner_unique, token) VALUES (\'{}\',\'{}\');'.format(unique_id, token)
        cursor.execute(query)
    else:
        query = 'UPDATE tokens SET token=\'{}\' WHERE owner_unique=\'{}\';'.format(token, unique_id)
        cursor.execute(query)

    cursor.close()

    return token