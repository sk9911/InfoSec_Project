from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

key = RSA.import_key(open('public.pem').read())

file_in = open('message.txt', 'rb')
message = file_in.read()
file_in.close()

file_in = open('signature.pem', 'rb')
signature = file_in.read()
file_in.close()

hash = SHA256.new(message)

try:
    PKCS115_SigScheme(key).verify(hash, signature)
    print("The signature is valid.")
except (ValueError, TypeError):
    print("The signature is not valid.")