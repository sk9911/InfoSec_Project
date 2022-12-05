from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import os

message = b'This is the message to be verified'
key = RSA.import_key(open('private.pem').read())
hash = SHA256.new(message)

signature = PKCS115_SigScheme(key).sign(hash)


def sign(message, fname, key=key):
    try:
        hash = SHA256.new(message)
        signature = PKCS115_SigScheme(key).sign(hash)
        file_out = open(fname, 'wb')
        file_out.write(signature)
        file_out.close()
        return str(os.path.abspath(fname))
    except:
        return TypeError