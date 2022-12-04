#Create a class name User having attributes id,name,email,password,role

class UserDatabase:
    def __init__(self):
        self.users = {}

    def create(self, user):
        self.users[user.email] = user

    def read(self, email):
        user = self.users.get(email)
        if(user == None):
            return None
        else:
            return {
                "name": user.name,
                "email": user.email,
                "account": user.account
            }

    def update(self, user):
        user = self.users.get(user.email)
        if(user == None):
            return None
        else:
            self.users[user.email] = user
            return {
                "name": user.name,
                "email": user.email,
                "account": user.account
            }

    def delete(self, email):
        return self.users.pop(email)

    def verify_password(self,email,password):
        user = self.users.get(email)
        if(user == None):
            return None
        
        # Matching Algorithm
        elif user["password"] == password:
            return True
        else:
            return False

    