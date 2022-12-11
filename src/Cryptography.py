from ecdsa import SigningKey, BadSignatureError
import hashlib
import base64

class Cryptography:
    def __init__(self):
        self._private_key = SigningKey.generate()
        self._public_key = self._private_key.verifying_key

    def sign_message(self, message:str):
        msg_hash = hashlib.sha256(message.encode('utf-8')).digest()
        signature = self._private_key.sign(msg_hash)
        # print("RAW SIGNATURE", signature, type(signature))
        return str(base64.b64encode(signature), 'utf8')
    
    def verify_signature(self, message:str, signature:str):
        msg_hash = hashlib.sha256(message.encode('utf-8')).digest()
        sig = base64.b64decode(bytes(signature, 'utf8'))
        # print("DECODED SIG", sig, type(sig))
        try:
            assert self._public_key.verify(sig, msg_hash)
            return True
        except (BadSignatureError):
            return False

# def main():
#     c = Cryptography()
#     m = "abcd"
#     s = c.sign_message(m)
#     # print("OUT SIGNATURE", s, type(s))
#     v = c.verify_signature(m, s)
#     print(v)
#     v = c.verify_signature("dddd", s)
#     print(v)

# if __name__ == "__main__":
#     main()