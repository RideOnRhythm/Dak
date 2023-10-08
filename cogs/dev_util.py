import io
import re
import sys

import aiohttp
from PIL import Image
import discord
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from discord.ext import commands
from assets.cog_list import cog_list
import subprocess

model = tf.keras.models.load_model("299x299.h5", custom_objects={"KerasLayer": hub.KerasLayer},
                                   compile=False)


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
    async def detect(self, ctx, url):
        url = url.strip("<>")

        if re.match("https://www.reddit.com/r/.*/comments/.*/.*/", url):
            result = subprocess.check_output(["gallery-dl", url, "-g"], shell=True, stderr=sys.stdout).decode()
            url = result.strip().split("\n")[-1]

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                bytes_im = io.BytesIO(await resp.read())

        image = Image.open(bytes_im)
        image = image.resize((299, 299))
        image = image.convert("RGB")
        array = np.array(image, dtype=np.float64)
        array /= 255.0
        array = np.stack([array], axis=0)

        model_preds = model.predict(array)
        value = model_preds[0][1]

        await ctx.send(f"{value:.2%}")

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
