# paytm_gateway/checksum.py

import base64
import string
import random
import hashlib
from Crypto.Cipher import AES

IV = '@@@@&&&&####$$$$'
BLOCK_SIZE = 16

def generateRandomString(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def encrypt(input, key):
    input = pad(input)
    c = AES.new(key.encode('utf-8'), AES.MODE_CBC, IV.encode('utf-8'))
    encrypted = c.encrypt(input.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt(encrypted, key):
    encrypted = base64.b64decode(encrypted)
    c = AES.new(key.encode('utf-8'), AES.MODE_CBC, IV.encode('utf-8'))
    decrypted = c.decrypt(encrypted).decode('utf-8')
    return unpad(decrypted)

def pad(data):
    length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + chr(length) * length

def unpad(data):
    last_char = ord(data[-1])
    return data[:-last_char]

def generateSignature(params, key):
    string = getStringByParams(params)
    return encrypt(string, key)

def verifySignature(params, key, checksum):
    string = getStringByParams(params)
    paytm_hash = decrypt(checksum, key)
    return string == paytm_hash

def getStringByParams(params):
    params_string = ''
    for key in sorted(params.keys()):
        if key != 'CHECKSUMHASH' and params[key] != '':
            params_string += str(params[key]) + '|'
    return params_string[:-1]
