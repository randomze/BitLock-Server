from auth import validation
from hashlib import sha1
from passlib.hash import sha256_crypt

def loginOrRegistration(cursor, email, password, secret, mode):
    hashed_pw = sha256_crypt.hash(password)
    
    unique = ''

    if mode == "registration":
        mod = sha1()
        mod.update(email.encode())
        unique = mod.hexdigest()
        query = 'INSERT INTO users (email, hashed_pw, unique_hash) VALUES (\'{}\', \'{}\', \'{}\');'.format(email, hashed_pw, unique)
        cursor.execute(query)
    elif mode == "login":
        query = 'SELECT hashed_pw, unique_hash FROM users WHERE email=\'{}\';'.format(email)
        cursor.execute(query)
        hashed_password, unique = cursor.fetchone()
        if not sha256_crypt.verify(password, hashed_password):
            return None

    token = validation.generateToken(cursor, unique, secret)

    return (token, unique)