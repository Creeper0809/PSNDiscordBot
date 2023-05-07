import discord
from discord.ext import commands
import json
import requests
import Datamodel
from sqlalchemy.future import engine
import RPGDatamodel
from sqlalchemy.orm import sessionmaker
import random


def setup(app):
    async def get_profile(user_id, ctx, a):
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
            Profile = json.loads(response.text)  ## json의 형식을 파이썬의 객체로 변환한다
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

            embed = discord.Embed(title=f"유저 {Profile['handle']}님의 프로필 정보", description=f"티어: {tier[Profile['tier']]}\n"
            f"Ranking: {Profile['rank']}\n"f"Rating: {Profile['rating']}\n"f"EXP: {Profile['exp']}\n"f"PROFILE: {Profile['profileImageUrl']}\n",)
            file = discord.File(f"image/baekjoon_tear/{Profile['tier']}.png", filename="image.png")
            embed.set_thumbnail(url='attachment://image.png')
            if a == 1:
                await ctx.send(file=file, embed=embed)
            if a == 2:
                return True

    async def get_problem(problem_id, ctx):
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
            embed = discord.Embed(title=problem['titleKo'],
            url=f"https://www.acmicpc.net/problem/{problem['problemId']}",
            description=f"문제번호:{problem['problemId']}\n"f"채점가능여부: {problem['isSolvable']}\n"f"맞은 사람 수: {problem['acceptedUserCount']}\n"
            f"평균 시도 횟수: {problem['averageTries']}\n")
            file = discord.File(f"image/baekjoon_tear/{problem['level']}.png", filename="image.png")
            embed.set_thumbnail(url='attachment://image.png')
            await ctx.send(file=file, embed=embed)
    async def get_solved(user_id, ctx):  ## user_id가 푼 문제 목록들을 가장 레벨이 높은 순으로 보여줌
        url = f"https://solved.ac/api/v3/search/problem?query=solved_by%3A{user_id}&sort=level&direction=desc"
        response = requests.get(url)
        if response.status_code == requests.codes.ok:
            tier_emoge = {
                0: "1100320160918818907", 1: "1100320165171839046", 2: "1100320168485322772", 3: "1100320171232612385",
                4: "1100320175502393456", 5: "1100320178924961863", 6: "1100320181873541232", 7: "1100320185392570438",
                8: "1100320190065029160", 9: "1100320194259320842", 10: "1100320197799313458", 11: "1100320200890515506",
                12: "1100320204573114428", 13: "1100320208796799036", 14: "1100320212814934137", 15: "1100320214840782859",
                16: "1100320218808598538", 17: "1100320222331813888", 18: "1100320224307335189", 19: "1100320227515957318",
                20: "1100320230120636501", 21: "1100320232578482298", 22: "1100320235812294666", 23: "1100320237649416232",
                24: "1100320240769978419", 25: "1100320242573520949", 26: "1100320245161414728", 27: "1100320247594090536",
                28: "1100320251020840971", 29: "1100320253772316743", 30: "1100320255496175746", 31: "1100320258734182410"
            }
            solved = json.loads(response.content.decode('utf-8'))
            count = solved.get('count')
            items = solved.get('items')
            title = ''
            tier2 = ''
            title_url = ''
            embed = discord.Embed(title=f"유저 {user_id}님의 푼 문제")
            for i in items[:10]:
                emoji_id = discord.utils.get(app.emojis, id=int(tier_emoge[i['level']]))
                tier2 += f"{emoji_id}\n"
                if len(i['titleKo']) > 7 :
                    title += f"[{i['titleKo'][:7]}...](https://www.acmicpc.net/problem/{i['problemId']})\n"
                else :
                    title += f"[{i['titleKo']}](https://www.acmicpc.net/problem/{i['problemId']})\n"
            embed.add_field(name="제목", value=title.rstrip())
            embed.add_field(name="티어", value=tier2.rstrip())
            await ctx.send(embed=embed)
    async def get_random(ctx, tier, random) : ## 백준 랜덤에 티어를 붙이면 티어에 따라 한국어 문제를 랜덤으로 뽑아 사용자에게 전달한다.
        url = f"https://solved.ac/api/v3/search/problem?query=tier:{tier}&%ko"
        response = requests.get(url)
        if not response.status_code == requests.codes.ok:
            return await ctx.send("예상치 못한 오류가 발생했습니다")
        if response.status_code == requests.codes.ok :
            solved = json.loads(response.content.decode('utf-8'))
            items = solved.get('items')
            rand = random.choice(items)
            embed = discord.Embed(title=f"{rand['titleKo']}",
            url=f"https://www.acmicpc.net/problem/{rand['problemId']}",description=f"문제번호:{rand['problemId']}\n"
            f"채점가능여부:{rand['isPartial']}\n"f"맞은 사람 수:{rand['acceptedUserCount']}\n"f"평균 시도 횟수:{rand['averageTries']}\n")
            file = discord.File(f"image/baekjoon_tear/{rand['level']}.png", filename="image.png")
            embed.set_thumbnail(url='attachment://image.png')
            await ctx.send(file=file,embed=embed)
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
    async def 문제번호(ctx,problem_number: str) :
        await get_problem(problem_number,ctx)
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
    async def 푼문제(ctx, user_id:str) :
        await get_solved(user_id,ctx)
    @beakjoon.command(name='랜덤')
    async def 랜덤(ctx, *, args) :
        first_word = args.split()[0]
        if first_word.startswith('브론즈') :
            await get_random(ctx, 'b',random)
        elif first_word.startswith('실버') :
            await get_random(ctx, 's',random)
        elif first_word.startswith('골드') :
            await get_random(ctx, 'g',random)
        elif first_word.startswith('플레') :
            await get_random(ctx, 'p',random)
        elif first_word.startswith('다이아') :
            await get_random(ctx, 'd',random)
        elif first_word.startswith('루비') :
            await get_random(ctx, 'r',random)
        else :
            await ctx.send("잘못된 명령어입니다")
