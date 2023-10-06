from discord.ext import commands
from discord.ext import tasks


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.save_db.start()

    @tasks.loop(seconds=5)
    async def save_db(self):
        await self.bot.database.save()


async def setup(bot):
    await bot.add_cog(Tasks(bot))
