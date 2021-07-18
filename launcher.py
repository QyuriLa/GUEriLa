import os
import logging

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Logging
logging.basicConfig(level=logging.INFO)

# Settings
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(
    command_prefix='!@',
    command_attrs=dict(hidden=True),
)


@bot.event
async def on_ready():
    print("===디스코드 접속 완료===")

@bot.command(name="새로고침")
async def reload_commands(ctx, extension=None):
    if extension is None: # extension이 None이면 (그냥 !리로드 라고 썼을 때)
        for filename in os.listdir("Cogs"):
            if filename.endswith(".py"):
                bot.unload_extension(f"Cogs.{filename[:-3]}")
                bot.load_extension(f"Cogs.{filename[:-3]}")
                await ctx.send("Cogs 새로고침 성공")

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

bot.run(TOKEN)
