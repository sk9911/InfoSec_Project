#Create a class name database having functions create,read,update,delete
#

class Database:

    def __init__(self):
        self.db = []

    def create(self, req):
        self.db.append(req)

    def read(self, id):
        for req in self.db:
            if req.id == id:
                return req

    def update(self, id, req):
        for i in range(len(self.db)):
            if self.db[i].id == id:
                self.db[i] = req

    def delete(self, id):
        for i in range(len(self.db)):
            if self.db[i].id == id:
                del self.db[i]