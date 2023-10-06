# Currency v0.1

import discord
from discord.ext import commands


class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["c", "bal", "balance"])
    async def coins(self, ctx, member: discord.Member = None):
        # If no member is specified, the member is the command author
        if member is None:
            member = ctx.author

        # Create embed
        embed = discord.Embed(color=discord.Color.yellow())
        embed.set_author(name=f"{member.display_name}'s Coin Balance", icon_url=member.avatar.url)

        # Get coin balance from database
        coin_bal = await self.bot.database.get_member_coins(member)
        embed.add_field(name="Coins :coin::", value=coin_bal)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Currency(bot))
