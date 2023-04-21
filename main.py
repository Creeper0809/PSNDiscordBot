import os

import pymysql

import Baekjoon
import CommonCommand
import discord
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
PREFIX = '!'
app = commands.Bot(command_prefix=PREFIX, intents=intents)
load_dotenv()

mysql = pymysql.connect(
    host=os.environ.get("HOST"),
    port=int(os.environ.get("PORT")),
    user=os.environ.get("USER"),
    password=os.environ.get("PASSWORD"),
    database=os.environ.get("DATABASE")
)

Baekjoon.setup(app,mysql)
CommonCommand.setup(app,mysql)


@app.event
async def on_ready():
    print('Done')
    await app.change_presence(status=discord.Status.online, activity=None)

if __name__=="__main__":
  app.run(os.environ.get("TOKEN"))
