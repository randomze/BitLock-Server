from auth import validation
from hashlib import sha1
from passlib.hash import sha256_crypt

def loginOrRegistration(cursor, email, password, secret, mode):
    hashed_pw = sha256_crypt.hash(password)
    
    unique_id = ''

    if mode == "registration":
        mod = sha1()
        mod.update(email.encode())
        unique_id = mod.hexdigest()
        query = 'INSERT INTO users (email, hashed_pw, unique_hash) VALUES (\'{}\', \'{}\', \'{}\');'.format(email, hashed_pw, unique_id)
        cursor.execute(query)
    elif mode == "login":
        query = 'SELECT hashed_pw, unique_hash FROM users WHERE email=\'{}\';'.format(email)
        cursor.execute(query)
        hashed_password, unique_id = cursor.fetchone()
        if not sha256_crypt.verify(password, hashed_password):
            return None

    token = validation.generateToken(cursor, unique_id, secret)

    return (token, unique_id)