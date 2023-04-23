import discord
from discord.ext import commands
import json
import requests
import random
import Datamodel
from sqlalchemy.future import engine
import RPGDatamodel
from sqlalchemy.orm import sessionmaker

async def get_profile(user_id,ctx,a):
    global Profile
    url = "https://solved.ac/api/v3/user/show"
    params = {
        "handle": user_id
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(url, params=params, headers=headers)

    if not response.status_code == requests.codes.ok:
        return False
    if response.status_code == requests.codes.ok:
        Profile = json.loads(response.text) ## json의 형식을 파이썬의 객체로 변환한다
        tier = {
                1: 'Bronze V', 2: 'Bronze IV', 3: 'Bronze III', 4: 'Bronze II', 5: 'Bronze I', 6: 'Silver V',
                7: 'Silver IV', 8: 'Silver III',
                9: 'Silver II', 10: 'Silver I', 11: 'Gold V', 12: 'Gold IV', 13: 'Gold III', 14: 'Gold II',
                15: 'Gold I', 16: 'Platinum V',
                17: 'Platinum IV', 18: 'Platinum III', 19: 'Platinum II', 20: 'Platinum I', 21: 'Diamond V',
                22: 'Diamond IV', 23: 'Diamond III',
                24: 'Diamond II', 25: 'Diamond I', 26: 'Ruby V', 27: 'Ruby IV', 28: 'Ruby III', 29: 'Ruby II',
                30: 'Ruby I', 31: 'Master'
            }

        embed = discord.Embed(title=f"유저 {Profile['handle']}님의 프로필 정보",description=f"티어: {tier[Profile['tier']]}\n"
        f"Ranking: {Profile['rank']}\n"f"Rating: {Profile['rating']}\n"f"EXP: {Profile['exp']}\n"f"PROFILE: {Profile['profileImageUrl']}\n", )
        file = discord.File(f"image/baekjoon_tear/{Profile['tier']}.png", filename="image.png")
        embed.set_thumbnail(url='attachment://image.png')
        if a == 1 :
            await ctx.send(file=file, embed=embed)
        if a == 2 :
            return True
async def get_solved(user_id,ctx):   ## user_id가 푼 문제 목록들을 가장 레벨이 높은 순으로 보여줌
    url = f"https://solved.ac/api/v3/search/problem?query=solved_by%3A{user_id}&sort=level&direction=desc"
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        tier = {
            1: 'Bronze V', 2: 'Bronze IV', 3: 'Bronze III', 4: 'Bronze II', 5: 'Bronze I', 6: 'Silver V',
            7: 'Silver IV', 8: 'Silver III',
            9: 'Silver II', 10: 'Silver I', 11: 'Gold V', 12: 'Gold IV', 13: 'Gold III', 14: 'Gold II',
            15: 'Gold I', 16: 'Platinum V',
            17: 'Platinum IV', 18: 'Platinum III', 19: 'Platinum II', 20: 'Platinum I', 21: 'Diamond V',
            22: 'Diamond IV', 23: 'Diamond III',
            24: 'Diamond II', 25: 'Diamond I', 26: 'Ruby V', 27: 'Ruby IV', 28: 'Ruby III', 29: 'Ruby II',
            30: 'Ruby I', 31: 'Master'
        }
        solved = json.loads(response.content.decode('utf-8'))
        count = solved.get('count')
        items = solved.get('items')
        title = ''
        tier2 = ''
        title_url = ''
        embed = discord.Embed(title=f"유저 {user_id}님의 푼 문제")
        for i in items[:10] :
            tier2 += f"{tier[i['level']]}\n"
            title += f"[{i['titleKo']}](https://www.acmicpc.net/problem/{i['problemId']})\n"
        file = discord.File(f"image/baekjoon_tear/{i['level']}.png", filename="image.png")
        embed.add_field(name="제목", value=title.rstrip())
        embed.add_field(name="티어",value=tier2.rstrip())
        embed.set_thumbnail(url='attachment://image.png')
        await ctx.send(file=file, embed=embed)

async def get_problem(problem_id,ctx) :
    url = "https://solved.ac/api/v3/problem/show"
    params = {
        "problemId": problem_id
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(url, params=params, headers=headers)
    if not response.status_code == requests.codes.ok:
        await ctx.send("문제의 대한 정보가 없습니다")
    if response.status_code == requests.codes.ok:
        problem = json.loads(response.text)
        embed = discord.Embed(title=problem['titleKo'], url=f"https://www.acmicpc.net/problem/{problem['problemId']}",
        description=f"문제번호:{problem['problemId']}\n"f"채점가능여부: {problem['isSolvable']}\n"f"맞은 사람 수: {problem['acceptedUserCount']}\n"
        f"평균 시도 횟수: {problem['averageTries']}\n")
        file = discord.File(f"image/baekjoon_tear/{problem['level']}.png", filename="image.png")
        embed.set_thumbnail(url='attachment://image.png')
        await ctx.send(file=file, embed=embed)

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
    async def 유저정보(ctx,user:str) :
        if user.startswith('<@') :
            user = user.replace('<@', '')
            user = user.replace('>', '')
            User: Datamodel.User = Datamodel.get_user(user)
            if User.baekjoon_id == "" :
                await ctx.send("해당 멘션에는 백준 아이디가 등록되어 있지 않습니다")
            else :
                await get_profile(Datamodel.get_user(user).baekjoon_id,ctx,1)
                ## 이미 아이디 등록할 때부터, 검증이 되기 때문에 result로 검증할 필요가 없다
        else :
            result = await get_profile(user,ctx,1)
            if not result :
                await ctx.send("프로필 정보를 찾을 수 없습니다.")

    @beakjoon.command(name='문제번호')
    async def 문제번호(ctx,problem_number: str):
        await get_problem(problem_number,ctx)

    @beakjoon.command(name='랜덤')
    async def 랜덤(ctx):
        await get_problem(random.randrange(1000,27892),ctx)

    @beakjoon.command(name='아이디등록')
    async def 아이디등록(ctx, baekjoonId:str) :
        user : Datamodel.User = Datamodel.get_user(ctx.message.author.id)
        if user.baekjoon_id != "" :
            await ctx.send("이미 아이디가 등록되엇습니다.")
            return
        if user is None :
            await ctx.send("회원가입을 먼저 해주세요")
            return
        result = await get_profile(baekjoonId,ctx,2)
        if result :
            Datamodel.update_userByUserClass(user,baekjoonId)
            await ctx.send("아이디가 등록되었습니다.")
        else :
            await ctx.send("백준에 없는 아이디입니다.")

    @beakjoon.command(name='푼문제')
    async def 푼문제(ctx, user_id:str):
        await get_solved(user_id,ctx)

        //