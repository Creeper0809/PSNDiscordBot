import asyncio
import random
from collections import deque

import discord
import RPGDatamodel
import Skills

combat_user = dict()


def setup(app):
    @app.event
    async def on_reaction_add(reaction, user):
        if user.bot:
            return
        user_id = str(user.id)
        if user_id in combat_user:
            if reaction.message.id == combat_user[user_id]["임베드"]:
                combat_user[user_id]["나가기"] = True

    @app.group(name = "던전")
    async def dungeon(ctx):
        user: RPGDatamodel.UserRPGInfo = RPGDatamodel.get_userRPGInfo(ctx.message.author.id)
        if user is None:
            await ctx.send('이 컨텐츠를 즐기기전에 회원가입부터 하십시오')
            return
        if ctx.invoked_subcommand is not None:
            return
        embed = discord.Embed(title="PWN봇의 RPG!",
                              description="더 자세한 명령어는 //던전 {도움말,도움,help}")
        await ctx.send(embed = embed)

    @dungeon.command(aliases = ["도움말","도움","help"])
    async def dungeon_help(ctx):
        embed = discord.Embed(title="RPG 명령어")
        commands = "//던전 입장 {던전 종류 중 하나} - 던전에 입장합니다.\n"
        commands += "//던전 내정보 - 내 정보를 봅니다.\n"
        commands += "//던전 내인벤 - 내 인벤을 엽니다.\n"
        commands += "//던전 내장비 - 내 장착중인 장비를 봅니다.\n"
        commands += "//던전 설명 {아이템 이름} - 아이템의 대한 설명을 보여줍니다.\n"
        commands += "//던전 아이템사용 {아이템 이름} - 선택한 아이템을 장착/사용합니다.\n"
        commands += "//던전 이름짓기 {이름} - 이름을 변경합니다.\n"
        embed.add_field(name="명령어 목록",value=commands,inline=False)
        embed.add_field(name="디버그 명령어",value="//던전 체력회복")
        embed.add_field(name="미완성 명령어", value="")
        await ctx.send(embed = embed)
    @dungeon.command(name = "입장")
    async def dungeon_join(ctx,message):
        userinfo: RPGDatamodel.UserRPGInfo = RPGDatamodel.get_userRPGInfo(ctx.message.author.id)
        if userinfo.id in combat_user:
            await ctx.send('이미 전투중입니다')
            return
        if userinfo.now_hp == 0:
            await ctx.send('체력회복부터 해주십시오')
            return
        dungeon : RPGDatamodel.Dungeon_info = RPGDatamodel.get_dungeon(message)
        if dungeon is None:
            await ctx.send('없는 던전입니다.')
            return
        monsters = dungeon.spawn_points
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
        await embedMessage.add_reaction('❎')

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ['✅', '❎']
        try:
            reaction, user = await app.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('입력 시간 초과!')
            return
        else:
            if reaction.emoji ==  '❎':
                await ctx.send('던전 입장 취소')
                return

        if dungeon.min_level > userinfo.level:
            await ctx.send("넌 아직 입장 할 수 없는 레벨이다")
            return

        combat_user[userinfo.id] = {
            "나가기" : False,
            "임베드" : embedMessage.id
        }

        await embedMessage.clear_reactions()

        embed.set_field_at(0,name="내 정보",value=":heart: 체력:%20s\n" % f"{userinfo.now_hp}/{userinfo.hp}",inline=False)
        embed.set_field_at(1,name="진행 상황", value="", inline=False)

        await embedMessage.edit(embed=embed)
        await embedMessage.add_reaction("⛔")
        events = [fightEvent,Chest]
        queue = deque(maxlen=5)
        while userinfo.now_hp != 0 and not combat_user[userinfo.id]["나가기"]:
            random_sleep = random.randint(0,10)
            await asyncio.sleep(random_sleep)
            event = random.choice(events)
            queue.append(await event(ctx,userinfo,dungeon))
            combat_text = "```"
            for i in range(len(queue)):
                combat_text+=queue[i]+'\n'
            combat_text += "```"
            embed.set_field_at(0,name= "내 정보",value=":heart: 체력:%20s\n" % f"{userinfo.now_hp}/{userinfo.hp}",inline=False)
            embed.set_field_at(1,name="진행 상황",value=combat_text,inline=False)
            await embedMessage.edit(embed = embed)
        await ctx.send("던전에서 나왔다.")
        del combat_user[userinfo.id]

    @dungeon.command(name="설명")
    async def dungeon_exit(ctx,message):
        if str.isdigit(message):
            item = RPGDatamodel.getItem(int(message))
        else:
            item = RPGDatamodel.getItem(message)
        if item is None:
            await ctx.send("없는 아이템입니다")
            return
        await ctx.send(embed = item.getDiscription())

    @dungeon.command(name="내정보")
    async def my_info(ctx):
        user: RPGDatamodel.UserRPGInfo = RPGDatamodel.get_userRPGInfo(ctx.message.author.id)
        level : RPGDatamodel.Experience_table = RPGDatamodel.get_experimentTable(user)
        now = user.accumulated_exp - level.accumulated_experience
        embed = user.getDiscription()
        embed.set_field_at(1,name="EXP", value=f"{now}/{level.required_experience}", inline=True)
        await ctx.send(embed=embed)

    @dungeon.command(name="내인벤")
    async def my_inv(ctx):
        user: RPGDatamodel.UserRPGInfo = RPGDatamodel.get_userRPGInfo(ctx.message.author.id)
        embed =user.get_inv_info()
        await ctx.send(embed = embed)

    @dungeon.command(name="아이템사용")
    async def use_item(ctx,message):
        user: RPGDatamodel.UserRPGInfo = RPGDatamodel.get_userRPGInfo(ctx.message.author.id)
        item = RPGDatamodel.getItem(message)
        if item is None:
            return
        if not user.hasItem(item.id):
            await ctx.send("소지하고 있는 아이템이 아닙니다.")
            return

        text = item.use(user)
        await ctx.send(text)

    @dungeon.command(name = "내장비")
    async def 장착정보(ctx):
        user: RPGDatamodel.UserRPGInfo = RPGDatamodel.get_userRPGInfo(ctx.message.author.id)
        embed = user.get_equip_item_info()
        await ctx.send(embed = embed)

    @dungeon.command(name="이름짓기")
    async def 장착정보(ctx,message):
        user: RPGDatamodel.UserRPGInfo = RPGDatamodel.get_userRPGInfo(ctx.message.author.id)
        user.name = message
        RPGDatamodel.update_datamodel(user)
        await ctx.send(f"{message}로 이름 변경 완료")

    @dungeon.command()
    async def 체력회복(ctx):
        user: RPGDatamodel.UserRPGInfo = RPGDatamodel.get_userRPGInfo(ctx.message.author.id)
        user.now_hp = user.hp
        await ctx.send(f'{user.name}은 풀피가 됐다.')
        RPGDatamodel.update_datamodel(user)

    async def fightEvent(ctx, user : RPGDatamodel.UserRPGInfo, dungeon:RPGDatamodel.Dungeon_info):
        randomMonster : RPGDatamodel.Monster = RPGDatamodel.get_monster(random.choice(dungeon.spawn_points).name)
        print(randomMonster.droptable)
        embed_message = await ctx.send(embed = randomMonster.getDiscription())

        await embed_message.add_reaction('✅')
        await embed_message.add_reaction('❎')

        def check(reaction, users):
            return users == ctx.message.author and str(reaction.emoji) in ['✅', '❎']
        try:
            reaction, users = await app.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await embed_message.delete()
            return '도망을 선택했다'
        else:
            if reaction.emoji == '❎':
                await embed_message.delete()
                return '도망을 선택했다'

        combat_text = ""
        embed = discord.Embed(title="전투 시작!", color=discord.Color.red())
        embed.add_field(name=f"{randomMonster.name} 체력", value=f"{randomMonster.now_hp} / {randomMonster.hp}")
        embed.add_field(name=f"{user.name} 체력", value=f"{user.now_hp} / {user.hp}")
        embed.add_field(name="전투 텍스트", value=combat_text, inline=False)
        await embed_message.edit(embed=embed)

        def fight(who, target):
            text = ""
            damage = random.randint(int(who.attack * 0.9), int(who.attack * 1.1))
            target.now_hp = Skills.clamp(target.now_hp - damage, 0, target.hp)
            text += f"{target.name}이 {who.name}에 의해 {damage}의 대미지를 받았다 \n"
            text += f"현재 {target.name}의 체력은 {target.now_hp}\n"
            if target.now_hp == 0:
                return text
            damage = random.randint(int(target.attack*0.9), int(target.attack * 1.1))
            who.now_hp = Skills.clamp(who.now_hp - damage, 0, who.hp)
            text += f"{who.name}이 {target.name}에 의해 {damage}의 대미지를 받았다 \n"
            text += f"현재 {who.name}의 체력은 {who.now_hp}\n"
            return text

        async def editembed():
            embed.set_field_at(0, name=f"{randomMonster.name} 체력", value=f"{randomMonster.now_hp} / {randomMonster.hp}")
            embed.set_field_at(1, name=f"{user.name} 체력", value=f"{user.now_hp} / {user.hp}")
            embed.set_field_at(2, name="전투 텍스트", value=combat_text, inline=False)
            await embed_message.edit(embed=embed)

        while user.now_hp > 0 and randomMonster.now_hp > 0:
            await asyncio.sleep(1)
            user_speed = random.randint(user.speed,30 + user.speed)
            monster_speed = random.randint(randomMonster.speed, 30+randomMonster.speed)
            combat_text = fight(user, randomMonster) if user_speed > monster_speed else fight(randomMonster,user)
            await asyncio.gather(
                editembed()
            )

        if user.now_hp == 0:
            combat_text = f"{user.name}은 {randomMonster.name}에 의해 쓰러졌다.\n"
        else:
            combat_text = f"{user.name}은 {randomMonster.name}에게서 승리를 가져왔다! 레벨 업! {randomMonster.dropPWN}원 획득.\n"
            temp = RPGDatamodel.get_user(user.id)
            for i in randomMonster.droptable:
                random_num = random.uniform(0,100)
                if random_num <= i.probability:
                    item = RPGDatamodel.getItem(i.item_id)
                    RPGDatamodel.add_item_to_inventory(user.id,i.item_id,1)
                    combat_text += f"{item.name}을 획득했다!\n"
            temp.PWN += randomMonster.dropPWN
            RPGDatamodel.update_datamodel(temp)
            combat_text += await addExp(ctx, user, 500)
        await asyncio.gather(deleteEmbed(embed_message, 1))
        RPGDatamodel.update_datamodel(user)
        return combat_text

    async def Chest(ctx, user, *args):
        return "상자를 발견했다!"




async def deleteEmbed(embed_message,second):
    await asyncio.sleep(second)
    await embed_message.delete()


async def addExp(ctx,user:RPGDatamodel.UserRPGInfo,amount):
    send_message = ""
    user.accumulated_exp += amount
    level : RPGDatamodel.Experience_table = RPGDatamodel.get_experimentTable(user)
    send_message += f"{amount}의 경험치를 얻었다\n"
    if user.level == level.level:
        return send_message
    send_message += "레벨이 올랐다!" if level.level - user.level == 1 else f"레벨이 {level.level - user.level}만큼 올랐다!"
    user.stats_remaining += level.level - user.level
    user.level = level.level
    return send_message