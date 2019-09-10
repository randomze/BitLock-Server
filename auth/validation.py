from datetime import datetime
from auth import jwt
import json
import psycopg2

def authenticate(cursor, token, secret):
    valid, data = jwt.verifyJWT(token, secret)

    if valid:
        query = 'SELECT date_issued, expired FROM tokens WHERE token=\'{}\';'.format(token)
        cursor.execute(query)
        query_results = cursor.fetchone()
        cursor.close()
        if not query_results:
            return (False, 'no_token')
        else:
            #get the issue date for the token and if its been used yet from the database
            date_issued, expired = query_results

            #parse the date string into a proper date structure
            date_issued = datetime.strptime(date_issued, "%d/%m/%y %H:%M:%S")

            #do the same for the token data
            data = json.loads(data)
            token_date_issued = datetime.strptime(data['date_issued'], "%d/%m/%y %H:%M:%S")

            #check if the token date corresponds with the database one and check if it's not been used already
            if not token_date_issued == date_issued:
                return (False, 'invalid_token_date')
            elif expired:
                return (False, 'invalid_token_expired')
            else:
                return (True, data['uuid'])
    else:
        cursor.close()
        return (False, 'invalid_token_jwt')

def generateToken(cursor, uuid, secret):
    date_issued = datetime.now().strftime("%d/%m/%y %H:%M:%S")

    header = {}
    header['alg'] = 'HS256'
    header['typ'] = 'JWT'

    data = {}
    data['uuid'] = uuid
    data['date_issued'] = date_issued

    token = jwt.makeJWT(json.dumps(header), json.dumps(data), secret)

    query = 'INSERT INTO tokens (token, date_issued, used) VALUES (\'{}\', \'{}\', FALSE);'.format(token, date_issued)
    cursor.execute(query)

    return token
