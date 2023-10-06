from discord.ext import commands
from assets.cog_list import cog_list


class DevUtil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reload(self, ctx):
        for cog in cog_list:
            await self.bot.reload_extension(cog)

        await ctx.send("Reloaded cogs.")

    @commands.command()
    async def database(self, ctx):
        await ctx.send(self.bot.database.database)


async def setup(bot):
    await bot.add_cog(DevUtil(bot))
