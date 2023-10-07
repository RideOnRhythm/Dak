import discord
from discord.ext import commands
from assets.cog_list import cog_list


# Command check so only devs are allowed to use these commands
async def is_dev(ctx):
    return ctx.author.id in [994223267462258688, 748388929631289436, 556307832241389581]


class DevUtil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Useful for coding without having to restart the bot everytime
    @commands.command()
    @commands.check(is_dev)
    async def reload(self, ctx):
        for cog in cog_list:
            await self.bot.reload_extension(cog)

        await ctx.send("Reloaded cogs.")

    @commands.command()
    @commands.check(is_dev)
    async def database(self, ctx):
        await ctx.send(self.bot.database.database)

    @commands.command()
    @commands.check(is_dev)
    async def add_coins(self, ctx, member: discord.Member, coin_amount: int):
        await self.bot.database.add_member_coins(member, coin_amount)
        await ctx.send(f"Added **{coin_amount}** :coin: to {member.mention}'s balance.")

    @commands.command()
    @commands.check(is_dev)
    async def set_coins(self, ctx, member: discord.Member, coin_amount: int):
        await self.bot.database.set_member_coins(member, coin_amount)
        await ctx.send(f"Set {member.mention}'s balance to {coin_amount} :coin:.")


async def setup(bot):
    await bot.add_cog(DevUtil(bot))
