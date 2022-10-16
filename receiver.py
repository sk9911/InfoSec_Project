import utils
import json
import rsa

if __name__ == "__main__":
    with open("message.json", "r") as f:
        message = json.load(f)
    pubkey = rsa.PublicKey(message["pubkey"][0], message["pubkey"][1])
    data = message["data"]
    signature = message["signature"]
    print(signature.encode())