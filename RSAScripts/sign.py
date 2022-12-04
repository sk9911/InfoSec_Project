from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

message = b'This is the message to be verified'
key = RSA.import_key(open('private.pem').read())
hash = SHA256.new(message)

signature = PKCS115_SigScheme(key).sign(hash)

file_out = open('signature.pem', 'wb')
file_out.write(signature)
file_out.close()

file_out = open('message.txt', 'wb')
file_out.write(message)
file_out.close()