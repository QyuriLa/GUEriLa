import os
import random
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
    command_prefix='!grl ',
    command_attrs=dict(hidden=True),
)


@bot.event
async def on_ready():
    print("===디스코드 접속 완료===")

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

bot.run(TOKEN)
