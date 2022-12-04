import utils
import json
import datetime

def generate_message(data, pubkey, signature: bytes):
    message = {}
    message["data"] = data
    message["pubkey"] = (pubkey["n"], pubkey["e"])
    message["signature"] = signature[2:-1]
    
    try:
        with open("message.json", "w") as f:
            json.dump(message, f, indent=4)
            return True
    except:
        print("Error writing to file")
        return False

if __name__ == "__main__":
    pubkey, privkey = utils.get_keypair()
    student_name = input("Enter student name: ")
    student_id = input("Enter student ID: ")
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    doctor_name = input("Enter doctor name: ")
    data = f"{date_time} {student_name} {student_id} {doctor_name}"
    signature = utils.sign(data, privkey)
    generate_message(data, pubkey, signature)