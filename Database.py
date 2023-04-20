class database():
    userData = list()
    def find_user(self,id):
        for i in self.userData:
            if id == i.id:
                return i
        return None


    def add_user(self,author):
        id = author.id
        name = author.name
        if self.find_user(id) is not None:
            return False
        self.userData.append(user(id,name))
        return True


class user():
    id = ""
    name = ""
    point = 0
    def __init__(self,id,name):
        self.id = id
        self.name = name
        self.point = 0