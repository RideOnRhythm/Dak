import pickle

# File where the database is saved
DATABASE_FILE = "../database"


class Database:
    def __init__(self):
        self.database = {}

    async def save(self):
        with open(DATABASE_FILE, "wb") as f:
            pickle.dump(self.database, f)

    async def load(self):
        with open(DATABASE_FILE, "rb") as f:
            self.database = pickle.load(f)

    async def check_init_member(self, member):
        if "members" not in self.database:
            self.database["members"] = {}

        # Add member in database if they aren't in it
        if member.id not in self.database["members"]:
            self.database["members"][member.id] = {}

    async def check_init_member_field(self, member, field, default_value):
        if field not in self.database["members"][member.id]:
            self.database["members"][member.id][field] = default_value

    async def get_member_coins(self, member):
        await self.check_init_member(member)
        await self.check_init_member_field(member, "coin_balance", 0)

        return self.database["members"][member.id]["coin_balance"]

    async def add_member_coins(self, member, coin_amount):
        await self.check_init_member(member)
        await self.check_init_member_field(member, "coin_balance", 0)

        self.database["members"][member.id]["coin_balance"] += coin_amount

    async def set_member_coins(self, member, coin_amount):
        await self.check_init_member(member)
        await self.check_init_member_field(member, "coin_balance", 0)

        self.database["members"][member.id]["coin_balance"] = coin_amount
