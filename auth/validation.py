from datetime import datetime
from auth import jwt
import json
import psycopg2

def authenticate(cursor, unique_id, token, secret):
    valid, data = jwt.verifyJWT(token, secret)

    if valid:
        query = 'SELECT token, date_issued FROM tokens WHERE owner_unique=\'{}\';'.format(unique_id)
        cursor.execute(query)
        query_results = cursor.fetchone()
        cursor.close()
        if not query_results:
            return (False, 'owner_no_token')
        else:
            #get the issue date for the token and if its been used yet from the database
            token, date_issued = query_results

            #parse the date string into a proper date structure
            date_issued = datetime.strptime(date_issued, "%d/%m/%y %H:%M:%S")

            #do the same for the token data
            data = json.loads(data)
            token_date_issued = datetime.strptime(data['date_issued'], "%d/%m/%y %H:%M:%S")
            token_unique = data['owner_unique']

            #check if the token date corresponds with the database one and check if it's not been used already
            if not token_date_issued == date_issued:
                return (False, 'token_invalid_date')
            elif not token_unique == unique_id:
                return (False, 'token_different_owner')
            else:
                return (True, data['owner_unique'])
    else:
        cursor.close()
        return (False, 'token_bad_signature')

def generateToken(cursor, unique_id, secret):
    date_issued = datetime.now().strftime("%d/%m/%y %H:%M:%S")

    header = {}
    header['alg'] = 'HS256'
    header['typ'] = 'JWT'

    data = {}
    data['owner_unique'] = unique_id
    data['date_issued'] = date_issued

    token = jwt.makeJWT(json.dumps(header), json.dumps(data), secret)

    query = 'SELECT token FROM tokens WHERE owner_unique=\'{}\';'.format(unique_id)
    cursor.execute(query)

    result = cursor.fetchone()

    if not result:
        query = 'INSERT INTO tokens (owner_unique, token, date_issued) VALUES (\'{}\',\'{}\', \'{}\');'.format(unique_id, token, date_issued)
        cursor.execute(query)
    else:
        query = 'UPDATE tokens SET token=\'{}\' WHERE owner_unique=\'{}\';'.format(token, unique_id)
        cursor.execute(query)

    cursor.close()

    return token