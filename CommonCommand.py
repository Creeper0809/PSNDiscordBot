import datetime
import random

import discord

import Datamodel
import RPGDatamodel


def setup(app):

    @app.command()
    async def 회원가입(ctx):
        user = RPGDatamodel.get_user(ctx.message.author.id)
        if user is None:
            RPGDatamodel.add_user(ctx.message.author.id,ctx.message.author.name)
            await ctx.channel.send(f"{ctx.message.author.mention}님 회원가입을 추가합니다!")
        else:
            await ctx.channel.send("이미 가입 된 회원입니다")


    @app.command(name = "유저정보")
    async def 유저정보(ctx, user: discord.User):
        userinfo:Datamodel.User = Datamodel.get_user(user.id)
        if userinfo is None:
            await ctx.channel.send(f"{user.mention}은 없는 회원입니다")
            return

        await ctx.channel.send(f"{user.mention}은 {userinfo.PWN}원을 가지고 계십니다.")

    @app.command()
    async def 돈추가(ctx, message):
        info = Datamodel.get_user(ctx.message.author.id)
        if info is None:
            await ctx.channel.send(f"{ctx.message.author.mention}은 회원가입부터 해주십시오")
        if not str.isdigit(message):
            return
        info.point += int(message)
        await ctx.channel.send(f"{ctx.message.author.mention}은 {info.point}원을 가지고 계십니다.")


    @app.command()
    async def 가위바위보(ctx, message):
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


    @app.command()
    async def 하이(ctx):
        print()

        await ctx.send('Hello I am Bot!')


    @app.command()
    async def 출석체크(ctx):
        user : Datamodel.User = Datamodel.get_user(ctx.message.author.id)
        if user is None:
            await ctx.send('회원가입부터 해주십시오.')
            return
        attendance_check = datetime.datetime.strptime(user.attendance_check.strftime('%Y-%m-%d'), '%Y-%m-%d')
        current_date = datetime.datetime.now()
        delta = (current_date - attendance_check).days
        if delta == 0:
            temp = attendance_check.strftime('%m월-%d일')
            await ctx.send(f'다음날에 다시 출석체크를 시도해주세요 \n{temp}에 출석하셨습니다')
        else:
            user.PWN += 1000
            user.attendance_check = current_date
            RPGDatamodel.update_datamodel(user)
            await ctx.send(f'오늘도 출석해주셔서 감사합니다 계좌로 1000원 입급해드렸습니다 ')


    @app.command()
    async def 도움말(ctx):
        print("sad")
        embed = discord.Embed(title=도움말, description=도움말)
        result = "하이 : 봇이 인사해준다\n"\
                 "가위바위보 {가위,바위,보} : 봇이랑 가위바위보.\n"\
                 "회원가입 : 회원가입을 해야 유저 활동을 할 수 있다.\n"\
                 "유저보기 {유저 멘션} : 멘션한 유저의 정보를 볼 수 있다."
        embed.add_field(name="기본", value=result, inline=False)
        result = "돈추가 {수} : 돈을 수만큼 추가해준다"
        embed.add_field(name="디버그", value=result, inline=False)
        await ctx.send(embed=embed)