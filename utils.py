import hashlib
import rsa
import base64

def get_hash(data):
    if isinstance(data, bytes):
        return hashlib.sha1(data).hexdigest()
    elif isinstance(data, str):
        return hashlib.sha1(data.encode()).hexdigest()
    else:
        raise TypeError("data must be bytes or str")

def get_keypair():
    (pubkey, privkey) = rsa.newkeys(512)
    return (pubkey, privkey)

def sign(data, privkey):
    if isinstance(data, bytes):
        return rsa.sign(data, privkey, 'SHA-1')
    elif isinstance(data, str):
        return rsa.sign(data.encode(), privkey, 'SHA-1')
    else:
        raise TypeError("data must be bytes or str")

def verify(data, signature, pubkey):
    if isinstance(data, bytes):
        return rsa.verify(data, signature, pubkey)
    elif isinstance(data, str):
        return rsa.verify(data.encode(), signature, pubkey)
    else:
        raise TypeError("data must be bytes or str")

def encrypt(data, privkey):
    if isinstance(data, bytes):
        return rsa.encrypt(data, privkey)
    elif isinstance(data, str):
        return rsa.encrypt(data.encode(), privkey)
    else:
        raise TypeError("data must be bytes or str")
    
def decrypt(data, pubkey):
    if isinstance(data, bytes):
        return rsa.decrypt(data, pubkey).decode()
    elif isinstance(data, str):
        return rsa.decrypt(data.encode(), pubkey).decode()
    else:
        raise TypeError("data must be bytes")

if __name__ == "__main__":
    pubkey, privkey = get_keypair()
    data = "Hello, world!"
    signature = sign(data, privkey)
    # data = "Helloworld!"
    print(rsa.verify(data.encode(), signature, pubkey))