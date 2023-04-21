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
def setup(app,mysql):
    @app.command(aliases=['안녕', 'hi', '안녕하세요'])
    async def ping(ctx):
        await ctx.channel.send(f'{ctx.author.mention}님 안녕하세요!')

    @app.command(aliases=['백준'])
    async def roll(ctx, user_id: str):
        profile = get_profile(user_id)
        tier = {
            1: 'Bronze V',
            2: 'Bronze IV',
            3: 'Bronze III',
            4: 'Bronze II',
            5: 'Bronze I',
            6: 'Silver V',
            7: 'Silver IV',
            8: 'Silver III',
            9: 'Silver II',
            10: 'Silver I',
            11: 'Gold V',
            12: 'Gold IV',
            13: 'Gold III',
            14: 'Gold II',
            15: 'Gold I',
            16: 'Platinum V',
            17: 'Platinum IV',
            18: 'Platinum III',
            19: 'Platinum II',
            20: 'Platinum I',
            21: 'Diamond V',
            22: 'Diamond IV',
            23: 'Diamond III',
            24: 'Diamond II',
            25: 'Diamond I',
            26: 'Ruby V',
            27: 'Ruby IV',
            28: 'Ruby III',
            29: 'Ruby II',
            30: 'Ruby I',
            31: 'Master'
        }
        if profile is not None:
            message = f"유저 {user_id}님의 프로필 정보:\n"
            message += f"티어: {tier[profile['tier']]}\n"
            message += f"Ranking: {profile['rank']}\n"
            message += f"Rating: {profile['rating']}\n"
            message += f"exp: {profile['exp']}\n"
            await ctx.send(message)
        else:
            await ctx.send("프로필 요청 실패")
