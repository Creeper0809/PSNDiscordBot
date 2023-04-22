import asyncio
import random

import discord

import Datamodel

combat_user = dict()

def setup(app):
    @app.group(name = "던전")
    async def dungeon(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('잘못된 명령어입니다.')

    @dungeon.command(name = "입장")
    async def dungeon_join(ctx,message):
        userinfo: Datamodel.UserRPGInfo = Datamodel.get_userRPGInfo(ctx.message.author.id)

        if userinfo is None:
            await ctx.send('이 컨텐츠를 즐기기전에 회원가입부터 하십시오')
            return
        print(type(userinfo.id))
        if combat_user.get(userinfo.id,False):
            await ctx.send('이미 전투중입니다')
            return
        if userinfo.now_hp == 0:
            await ctx.send('체력회복부터 해주십시오')
            return
        dungeon : Datamodel.Dungeon_info = Datamodel.get_dungeon(message)
        if dungeon is None:
            await ctx.send('없는 던전입니다.')
            return

        dungeon,monsters = dungeon
        embed = discord.Embed(title=f"던전: {dungeon.name}",
                              description=f"{dungeon.description}")
        embed.add_field(name="입장 최소 레벨", value=dungeon.min_level)

        appearances = ""

        if len(monsters) > 0:
            for i in monsters[:len(monsters) - 1]:
                appearances += i.name + ", "
            appearances += monsters[len(monsters) - 1].name

        embed.add_field(name="출현 몬스터",value=appearances,inline=False)
        embedMessage = await ctx.send(embed = embed)
        await embedMessage.add_reaction('✅')
        await embedMessage.add_reaction('❌')

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ['✅', '❌']
        try:
            reaction, user = await app.wait_for('reaction_add', timeout=10.0, check=check)  # 해당 이모지를 추가한 유저가 60초 이내로 리액션을 달면 이벤트 발생
        except asyncio.TimeoutError:
            await ctx.send('Timeout!')  # 시간 초과시 메시지 전송
            return
        else:
            if reaction.emoji ==  '❌':# 리액션을 단 유저 정보 출력
                await ctx.send('던전 입장 취소')
                return

        if dungeon.min_level > userinfo.level:
            await ctx.send("넌 아직 입장 할 수 없는 레벨이다")
            return
        combat_user[userinfo.id] = True
        await ctx.send("던전 입장")
        while userinfo.now_hp != 0:
            random_sleep = random.randint(0,30)
            await asyncio.sleep(random_sleep)
            await fightEvent(ctx,userinfo,monsters)
        await ctx.send("체력을 다 했다.")
        combat_user[str(ctx.message.author.id)] = False

    @dungeon.command(name="퇴장")
    async def dungeon_exit(ctx):
        combat_user[str(ctx.message.author.id)] = False
        await ctx.send('던전 퇴장')

    @dungeon.command(name="내정보")
    async def my_info(ctx):
        user: Datamodel.UserRPGInfo = Datamodel.get_userRPGInfo(ctx.message.author.id)
        if user is None:
            await ctx.send('이 컨텐츠를 즐기기전에 회원가입부터 하십시오')
            return
        level : Datamodel.Experience_table = Datamodel.get_experimentTable(user)
        now = user.accumulated_exp - level.accumulated_experience

        spac = ""
        spac += ":heart: 체력:%20s\n" % f"{user.now_hp}/{user.hp}"
        spac += ":crossed_swords: 공격력:%20s\n" % f"{user.minattack}~{user.maxattack}"
        spac += ":magic_wand: 마법공격력:%20s\n" % "0~0"
        spac += ":shield: 방어력:%20s\n" % f"{user.defense}"
        spac += ":boot: 민첩도:%20s" % f"{user.speed}"

        embed = discord.Embed()
        embed.set_author(name=f"{user.name}의 정보")
        embed.add_field(name="레벨", value=f"{level.level}", inline=False)
        embed.add_field(name="EXP", value=f"{now}/{level.required_experience}", inline=True)
        embed.add_field(name="스펙", value= spac, inline=False)
        embed.add_field(name="-"*30, value="", inline=True)
        embed.add_field(name="남은 스탯", value=f"{user.stats_remaining}", inline=False)

        await ctx.send(embed=embed)

    @dungeon.command()
    async def 체력회복(ctx):
        user: Datamodel.UserRPGInfo = Datamodel.get_userRPGInfo(ctx.message.author.id)
        if user is None:
            await ctx.send('이 컨텐츠를 즐기기전에 회원가입부터 하십시오')
            return
        user.now_hp = user.hp
        await ctx.send(f'{user.name}은 풀피가 됐다.')
        Datamodel.update_datamodel(user)

    async def fightEvent(ctx,user,*args):
        monsters = args[0]
        randomMonster = monsters[random.randint(0,len(monsters)-1)]
        await ctx.send(f"무서운 몬스터 {randomMonster.name}이(가) 나타났다!")

        combat_text = ""
        embed = discord.Embed(title="전투 시작!", color=discord.Color.red())
        embed.add_field(name=f"{randomMonster.name} 체력", value=f"{randomMonster.now_hp} / {randomMonster.hp}")
        embed.add_field(name=f"{user.name} 체력", value=f"{user.now_hp} / {user.hp}")
        embed.add_field(name="전투 텍스트", value=combat_text, inline=False)
        embed_message = await ctx.send(embed=embed)

        def fight(who, target):
            text = ""
            damage = random.randint(who.minattack, who.maxattack + 1)
            target.now_hp = clamp(target.now_hp - damage, 0, target.hp)
            text += f"{target.name}이 {who.name}에 의해 {damage}의 대미지를 받았다 \n"
            text += f"현재 {target.name}의 체력은 {target.now_hp}\n"
            damage = random.randint(target.minattack, target.maxattack + 1)
            who.now_hp = clamp(who.now_hp - damage, 0, who.hp)
            text += f"{who.name}이 {target.name}에 의해 {damage}의 대미지를 받았다 \n"
            text += f"현재 {who.name}의 체력은 {who.now_hp}\n"
            return text

        async def editembed():
            embed.set_field_at(0, name=f"{randomMonster.name} 체력", value=f"{randomMonster.now_hp} / {randomMonster.hp}")
            embed.set_field_at(1, name=f"{user.name} 체력", value=f"{user.now_hp} / {user.hp}")
            embed.set_field_at(2, name="전투 텍스트", value=combat_text, inline=False)
            await embed_message.edit(embed=embed)

        while user.now_hp > 0 and randomMonster.now_hp > 0:
            userSpeed = random.randint(user.speed, 30)
            monsterSpeed = random.randint(randomMonster.speed, 30)
            if userSpeed > monsterSpeed:
                combat_text = fight(user, randomMonster)
            else:
                combat_text = fight(randomMonster, user)
            await asyncio.gather(
                editembed()
            )
            await asyncio.sleep(1)

        if user.now_hp == 0:
            await ctx.send(f"{user.name}은 {randomMonster.name}에 의해 쓰러졌다.")
        else:
            await ctx.send(f"{user.name}은 {randomMonster.name}에게서 승리를 가져왔다! 레벨 업! 1000원 획득")
            Datamodel.update_PWN(user.id, 1000)
            await asyncio.gather(
                addExp(ctx, user, 500)
            )

        await asyncio.gather(deleteEmbed(embed_message, 1))

        Datamodel.update_datamodel(user)



async def deleteEmbed(embed_message,second):
    await asyncio.sleep(second)
    await embed_message.delete()


def clamp(n, min_value, max_value):
    return max(min(n, max_value), min_value)


async def addExp(ctx,user:Datamodel.UserRPGInfo,amount):
    send_message = ""
    user.accumulated_exp += amount
    level : Datamodel.Experience_table = Datamodel.get_experimentTable(user)
    send_message += f"{amount}의 경험치를 얻었다\n"
    if user.level == level.level:
        await ctx.send(send_message)
        return
    send_message += "레벨이 올랐다!" if level.level - user.level == 1 else f"레벨이 {level.level - user.level}만큼 올랐다!"
    await ctx.send(send_message)
    user.stats_remaining += level.level - user.level
    user.level = level.level