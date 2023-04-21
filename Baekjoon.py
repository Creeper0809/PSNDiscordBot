import discord
from discord.ext import commands
import json
import requests

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
    @app.command(name='백준')
    async def beakjoon(ctx, option: str, *args) :
        if option == '유저정보' :
            await roll1(ctx,option,args[0])
        elif option == '문제번호' :
            await roll2(ctx,option,args[0])
        elif option == 'pvp요청' :
            await 아이디(ctx,option,args[0])
        else :
            await ctx.send("그런 명령어는 존재하지 않습니다.")
    async def roll1(ctx,option,user_id: str):
        if option == '유저정보' :
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
                await ctx.send("프로필 요청 실패")
    async def roll2(ctx,option,problem_number: str):
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

   '''
   
    async def 아이디(ctx, option, id: str):
        
        
        if id is not NULL :
   
   
   '''
