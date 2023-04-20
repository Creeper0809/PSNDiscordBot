import asyncio
import random

import Baekjoon
import Database
import discord
from discord.ext import commands

import RockSissorPaper

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
app = commands.Bot(command_prefix='/', intents=intents)

RockSissorPaper.setup(app)
Baekjoon.setup(app)

PREFIX = '/'

database = Database.database()

@app.event
async def on_ready():
    print('Done')
    await app.change_presence(status=discord.Status.online, activity=None)

@app.command()
async def 회원가입(ctx):
    if database.add_user(ctx.message.author):
        await ctx.channel.send(f"{ctx.message.author.mention}님 회원가입을 추가합니다!")
    else:
        await ctx.channel.send("이미 가입 된 회원입니다")

@app.command()
async def 유저보기(ctx,user : discord.User):
    info = database.find_user(user.id)
    if info is None:
        await ctx.channel.send(f"{user.mention}은 없는 회원입니다")
    await ctx.channel.send(f"{user.mention}은 {info.point}원을 가지고 계십니다.")

@app.command()
async def 돈추가(ctx,message):
    info = database.find_user(ctx.message.author.id)
    if info is None:
        await ctx.channel.send(f"{ctx.message.author.mention}은 회원가입부터 해주십시오")
    if not str.isdigit(message):
        return
    info.point += int(message)
    await ctx.channel.send(f"{ctx.message.author.mention}은 {info.point}원을 가지고 계십니다.")

@app.command()
async def 가위바위보(ctx,message):
    alias = ["가위", "바위", "보"]
    computer = alias[random.randint(0, len(alias) - 1)]
    player = message
    await ctx.channel.send("컴퓨터는 " + computer + "를 냈다")
    if (player == "가위" and computer == "보") or (player == "바위" and computer == "가위") or (
            player == "보" and computer == "바위"):
        result = "플레이어가 이겼다!"
    elif (player == "가위" and computer == "가위") or (player == "바위" and computer == "바위") or (
            player == "보" and computer == "보"):
        result = "플레이어와 컴퓨터가 비겼다"
    else:
        result = "플레이어가 졌다!"
    await ctx.channel.send(result)

s
@app.command()
async def 하이(ctx):
    print()
    await ctx.send('Hello I am Bot!')

if __name__=="__main__":
    app.run('')