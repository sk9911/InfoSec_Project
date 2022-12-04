#Create a class name User having attributes id,name,email,password,role

class UserDatabase:
    def __init__(self):
        self.users = []

    def create(self, user):
        self.users.append(user)

    def read(self, email):
        for user in self.users:
            if user.email == email:
                return {
                    "name":user.name,
                    "email" : user.email
                }

    def update(self, email, user):
        for i in range(len(self.users)):
            if self.users[i].email == email:
                self.users[i] = user

    def delete(self, email):
        for i in range(len(self.users)):
            if self.users[i].email == email:
                del self.users[i]

    def verify_password(self,email,password):
        for i in range(len(self.users)):
            if(self.users[i].email) == email:
                if(self.users[i].password) == password:
                    return True
                else:
                    return False
            else:
                return False

    