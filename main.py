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


async def main():
    print("Loading database...")
    await bot.database.load()

    # Load cogs from cog_list.py
    for cog in cog_list:
        print(f"Loading cog {cog}")
        await bot.load_extension(cog)

    print("Starting bot...")
    await bot.start(os.getenv("TOKEN"))


# TODO: connect 4 no space fix
asyncio.run(main())
