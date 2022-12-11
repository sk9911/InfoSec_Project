#Create a class name User having attributes id,username,password,role
from Models import User, UserView, Makeup, MakeupData, MRequest, MRequestData
from passlib.hash import bcrypt
from typing import List

class UserDatabase:
    def __init__(self):
        self.db = {}

    def get_all(self):
        return list(self.db.values())

    def create(self, user:User):
        if user.username in self.db:
            return None
        user.password = bcrypt.hash(user.password)
        self.db[user.username] = user
        return user

    def read(self, username:str):
        user = self.db.get(username)
        if not user:
            return None
        else:
            return UserView(username=user.username, account=user.account)

    # def update(self, updatedUser):
    #     user = self.db.get(user.username)
    #     if not user:
    #         return None
    #     else:
    #         self.db[user.username] = updatedUser
    #         return {
    #             "username": user.username,
    #             "account": user.account
    #         }

    # def delete(self, username:str):
    #     return self.db.pop(username)

    def authenticate(self,username:str,password:str):
        user = self.db.get(username)
        if not user:
            return None
        # Matching Algorithm
        if bcrypt.verify(password, user.password):
            return user
        else:
            return False
    
    def giveToken(self,username:str, tkn:str):
        self.db[username].token = tkn
        return self.db[username].token
    
    def takeToken(self,username:str):
        if self.db[username].token:
            self.db[username].token = None

#Create a class name database having functions create,read,update,delete

class MakeupDatabase:
    def __init__(self):
        self.db: List[Makeup] = []
    def size(self):
        return len(self.db)
    def get_all(self):
        return self.db
    def create(self, obj:Makeup):
        self.db.append(obj)
        return self.db[-1]
    def read(self, id):
        return self.db[id]
    def update(self, id, obj):
        self.db[id] = obj
        return self.db[id]
    # def delete(self, id):
    #     return self.db.pop(id)
    def get_prof(self,prof_username:str):
        return list(filter(lambda obj: obj.professor.username == prof_username, self.db))
    def get_open(self):
        return list(filter(lambda obj: obj.isOpen, self.db))
    def close_makeup(self,id:int):
        self.db[id].isOpen = False
        return self.db[id]
    
class RequestDatabase():
    def __init__(self):
        self.db = []
    def size(self):
        return len(self.db)
    def get_all(self):
        return self.db
    def create(self, obj:MRequest):
        self.db.append(obj)
        return self.db[-1]
    def read(self, id):
        return self.db[id]
    def update(self, id, obj):
        self.db[id] = obj
        return self.db[id]
    # def delete(self, id):
    #     return self.db.pop(id)
    def get_student(self,stud_username:str):
        return list(filter(lambda obj: obj.student.username == stud_username, self.db))
    def get_makeup(self,m_id:int):
        return list(filter(lambda obj: obj.makeup.id == m_id, self.db))