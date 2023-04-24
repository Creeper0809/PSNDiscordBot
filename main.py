import os
import pymysql
import Baekjoon
import CommonCommand
import discord
from discord.ext import commands
from dotenv import load_dotenv

import Datamodel
import RPGGame

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
PREFIX = '!'
app = commands.Bot(command_prefix=PREFIX, intents=intents)

Datamodel.makeDB()
Baekjoon.setup(app)
CommonCommand.setup(app)
RPGGame.setup(app)

@app.event
async def on_ready():
    print('Done')
    await app.change_presence(status=discord.Status.online, activity=None)

if __name__=="__main__":
  app.run(os.environ.get("TOKEN"))
