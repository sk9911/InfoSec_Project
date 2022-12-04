#Create a class name database having functions create,read,update,delete
#

class Database:

    def __init__(self):
        self.db = []

    def create(self, req):
        req[id] = len(db)
        self.db.append(req)

    def read(self, id):
        return self.db[id]

    def update(self, id, req):
        self.db[id] = req
        return self.db[id]

    def delete(self, id):
        return self.db.pop(id)
