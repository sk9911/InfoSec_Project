#Create a class name User having attributes id,username,password,role
from Models import User, UserView
from passlib.hash import bcrypt

class UserDatabase:
    def __init__(self):
        self.db = {}

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

    def delete(self, username:str):
        return self.db.pop(username)

    def authenticate(self,username:str,password:str):
        user = self.db.get(username)
        if not user:
            return None
        # Matching Algorithm
        if bcrypt.verify(password, user.password):
            return UserView(username=user.username, account=user.account)
        else:
            return False

    