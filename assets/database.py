import pickle

# File where the database is saved
DATABASE_FILE = "database"


class Database:
    def __init__(self):
        self.database = {}

    async def save(self):
        with open(DATABASE_FILE, "wb") as f:
            pickle.dump(self.database, f)

    async def load(self):
        with open(DATABASE_FILE, "rb") as f:
            self.database = pickle.load(f)
