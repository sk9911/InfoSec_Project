from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from Crypto.Hash import SHA256

class Cryptography:
    def __init__(self):
        self._private_key = RSA.generate(2048)
        self._public_key = self.private_key.publickey().export_key()

    def sign_message(self, message:str):
        msg_hash = SHA256.new(bytes(message))
        signature = PKCS115_SigScheme(self._private_key).sign(msg_hash)
        return signature
    
    def verify_signature(self, message:str, signature:str):
        msg_hash = SHA256.new(bytes(message))
        try:
            PKCS115_SigScheme(self._public_key).verify(msg_hash, signature)
            return True
        except (ValueError):
            return False
