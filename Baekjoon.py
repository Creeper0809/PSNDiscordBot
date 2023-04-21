import discord
from discord.ext import commands
import json
import requests
import random

def get_profile(user_id):
    url = "https://solved.ac/api/v3/user/show"
    params = {
        "handle": user_id
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == requests.codes.ok:
        return json.loads(response.text)
    else:
        return None

def get_problem(problem_id) :
    url = "https://solved.ac/api/v3/problem/show"
    params = {
        "problemId": problem_id
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == requests.codes.ok:
        return json.loads(response.text)
    else:
        return None

def setup(app):
    @app.group(name='백준')
    async def beakjoon(ctx) :
        if ctx.invoked_subcommand is None :
            await ctx.send("잘못된 명령어입니다.")
    @beakjoon.command(name = '도움말')
    async def 도움말(ctx) :
        embed = discord.Embed(title="도움말", description="/백준 유저정보 {백준 닉네임} : 백준의 닉네임을 가져옵니다.\n"
        "/백준 문제번호 {문제번호} : 백준의 문제번호를 입력하면, 문제에 대한 정보가 나옵니다.\n"
        "/백준 랜덤 : 백준의 문제에 대한 정보가 랜덤으로 나옵니다.\n")
        await ctx.send(embed=embed)
    @beakjoon.command(name = '유저정보')
    async def roll1(ctx,user_id: str):
        profile = get_profile(user_id)
        tier = {
            1: 'Bronze V', 2: 'Bronze IV', 3: 'Bronze III', 4: 'Bronze II', 5: 'Bronze I', 6: 'Silver V', 7: 'Silver IV', 8: 'Silver III',
            9: 'Silver II', 10: 'Silver I', 11: 'Gold V', 12: 'Gold IV', 13: 'Gold III', 14: 'Gold II', 15: 'Gold I', 16: 'Platinum V',
            17: 'Platinum IV', 18: 'Platinum III', 19: 'Platinum II', 20: 'Platinum I', 21: 'Diamond V', 22: 'Diamond IV', 23: 'Diamond III',
            24: 'Diamond II', 25: 'Diamond I', 26: 'Ruby V', 27: 'Ruby IV', 28: 'Ruby III', 29: 'Ruby II', 30: 'Ruby I', 31: 'Master'
        }
        if profile is not None:
            embed = discord.Embed(title=f"유저 {user_id}님의 프로필 정보",description=f"티어: {tier[profile['tier']]}\n"
            f"Ranking: {profile['rank']}\n"f"Rating: {profile['rating']}\n"f"EXP: {profile['exp']}\n"f"PROFILE: {profile['profileImageUrl']}\n", )
            file = discord.File(f"image/baekjoon_tear/{profile['tier']}.png", filename="image.png")
            embed.set_thumbnail(url='attachment://image.png')
            await ctx.send(file=file, embed=embed)
        else:
            await ctx.send("존재하지 않는 프로필 입니다.")
    @beakjoon.command(name='문제번호')
    async def roll2(ctx,problem_number: str):
        problem = get_problem(problem_number)
        if problem is not None:
            embed = discord.Embed(title=problem['titleKo'],url=f"https://www.acmicpc.net/problem/{problem['problemId']}",
            description=f"문제번호:{problem['problemId']}\n"f"채점가능여부: {problem['isSolvable']}\n"f"맞은 사람 수: {problem['acceptedUserCount']}\n"
            f"평균 시도 횟수: {problem['averageTries']}\n")
            file = discord.File(f"image/baekjoon_tear/{problem['level']}.png", filename="image.png")
            embed.set_thumbnail(url='attachment://image.png')
            await ctx.send(file=file, embed=embed)
        else:
            await ctx.send("문제의 대한 정보가 없습니다")

    @beakjoon.command(name='랜덤')
    async def roll3(ctx):
        rand = get_problem(random.randrange(1000,27892))
        if rand is not None:
            embed = discord.Embed(title=rand['titleKo'],url=f"https://www.acmicpc.net/problem/{rand['problemId']}",
            description=f"문제번호:{rand['problemId']}\n"f"채점가능여부: {rand['isSolvable']}\n"f"맞은 사람 수: {rand['acceptedUserCount']}\n"
            f"평균 시도 횟수: {rand['averageTries']}\n")
            file = discord.File(f"image/baekjoon_tear/{rand['level']}.png", filename="image.png")
            embed.set_thumbnail(url='attachment://image.png')
            await ctx.send(file=file, embed=embed)
        else:
            await ctx.send("문제의 대한 정보가 없습니다")

    @beakjoon.command(name='아이디등록')
    async def 아이디등록(ctx,beakjoon_id:str) :



