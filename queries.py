

class Queries:
    """ Class containing useful database queries """

    database_connection = None

    def __init__(self, database_connection):
        print("__init__()")
        self.database_connection = database_connection

