import base64
import hashlib
import hmac

def makeJWT(header, payload, secret):
    #encode both the header and the payload in base64 with a urlsafe alphabet
    encodedHeader = base64.urlsafe_b64encode(header.encode())
    encodedPayload = base64.urlsafe_b64encode(payload.encode())

    #calculate the signature
    signature = hmac.new(key = secret.encode(),
                         msg = str(encodedHeader + '.'.encode() + encodedPayload).encode(),
                         digestmod = hashlib.sha256).hexdigest().upper()

    #concatenate everything to get the token
    jwt = encodedHeader + '.'.encode() + encodedPayload + '.'.encode() + base64.urlsafe_b64encode(signature.encode())
    return jwt.decode()

def verifyJWT(token, secret):
    header, payload, signature = token.split('.')

    #recalculate the signature
    verification = hmac.new(key = secret.encode(),
                            msg = str(header.encode() + '.'.encode() + payload.encode()).encode(),
                            digestmod = hashlib.sha256).hexdigest().upper()

    #compare trusted signature with the one provided by the token and return appropriately
    if not verification == base64.urlsafe_b64decode(signature).decode():
        return (False, None)
    else:
        return (True, base64.urlsafe_b64decode(payload.encode()))