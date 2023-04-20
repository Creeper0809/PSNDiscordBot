import Baekjoon
import CommonCommand
import Database
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
PREFIX = '/'
app = commands.Bot(command_prefix=PREFIX, intents=intents)

Baekjoon.setup(app)
CommonCommand.setup(app)
database = Database.database()

@app.event
async def on_ready():
    print('Done')
    await app.change_presence(status=discord.Status.online, activity=None)

if __name__=="__main__":
    app.run('')