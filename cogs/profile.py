from discord.ext import commands


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["p", "prof"])
    async def profile(self, ctx):
        pass


async def setup(bot):
    await bot.add_cog(Profile(bot))
