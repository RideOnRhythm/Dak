from discord.ext import commands


class DevUtil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reload(self, ctx):
        # TODO: do this
        await ctx.send("Reloaded cogs.")


async def setup(bot):
    await bot.add_cog(DevUtil(bot))
