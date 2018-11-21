from oslo_db_learn.db import api

class App(object):

    def __init__(self):
        api.configure({'connection': 'mysql+pymysql://root:123@localhost:3306/test'})

    def create_company(self, data):
        """Create Foo object"""
        return(api.create_company(data))

if __name__ == '__main__':
    app = App()
    data = {"name":"ciro"}
    app.create_company(data)