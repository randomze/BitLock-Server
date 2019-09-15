from auth import validation
from hashlib import sha1
from passlib.hash import sha256_crypt

def loginOrRegistration(cursor, email, password, secret, mode):
    #encrypt password for storing in the database or comparing with the stored one
    hashed_pw = sha256_crypt.hash(password)

    unique_id = ''

    #check mode
    if mode == "registration":
        #calculate a unique id for the user
        mod = sha1()
        mod.update(email.encode())
        unique_id = mod.hexdigest()

        #insert into the database
        query = 'INSERT INTO users (email, hashed_pw, unique_hash) VALUES (\'{}\', \'{}\', \'{}\');'.format(email, hashed_pw, unique_id)
        cursor.execute(query)
    elif mode == "login":
        #fetch the encrypted password and unique user id from database
        query = 'SELECT hashed_pw, unique_hash FROM users WHERE email=\'{}\';'.format(email)
        cursor.execute(query)
        result = cursor.fetchone()

        #check if the user exists
        if result:
            #check if the password is correct
            hashed_password, unique_id = result
            if not sha256_crypt.verify(password, hashed_password):
                return None
        else:
            return None

    #generate an acess token
    token = validation.generateToken(cursor, unique_id, secret)

    return (token, unique_id)