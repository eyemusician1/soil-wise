import sqlite3

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        
    def connect(self):
        # TODO: Implement database connection
        return sqlite3.connect(self.db_path)
        
    def close(self):
        # TODO: Implement database connection closing
        pass