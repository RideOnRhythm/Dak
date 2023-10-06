import asyncio
import discord
import os
from discord.ext import commands
from assets.database import Database
from assets.cog_list import cog_list

# Dak bot initialization
bot = commands.Bot(
    command_prefix=["j.", "J.", "j,", "j", "J"],
    case_insensitive=True,
    intents=discord.Intents.all()
)
discord.utils.setup_logging()
bot.database = Database()
# TODO: Periodic saving in tasks.py


async def main():
    # Load cogs
    for cog in cog_list:
        print(f"Loading cog {cog}")
        await bot.load_extension(cog)

    # Start bot
    print("Starting bot...")
    await bot.start(os.getenv("token"))


asyncio.run(main())
