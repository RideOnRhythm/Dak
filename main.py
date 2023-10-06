import asyncio
import discord
import os
from discord.ext import commands

# Dak bot initialization
bot = commands.Bot(
    command_prefix=["j.", "J.", "j,", "j", "J"],
    case_insensitive=True,
    intents=discord.Intents.all()
)


async def main():
    # Load cogs
    print("Loading jishaku...")
    await bot.load_extension("jishaku")
    print("Loading developer utils...")
    await bot.load_extension("cogs.dev_util")
    print("Loading currency cog...")
    await bot.load_extension("cogs.currency")

    # Start bot
    print("Starting bot...")
    await bot.start(os.getenv("token"))


asyncio.run(main())
