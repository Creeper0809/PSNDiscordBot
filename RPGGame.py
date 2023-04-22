import asyncio
import random
import discord
import Datamodel

def setup(app):
    @app.group(name = "던전")
    async def dungeon(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('잘못된 명령어입니다.')

    @dungeon.command(name = "입장")
    async def dungeon_join(ctx):
        await ctx.send('던전 입장')

    @dungeon.command(name="퇴장")
    async def dungeon_exit(ctx):
        await ctx.send('던전 퇴장')

    @dungeon.command()
    async def 싸운다(ctx,message):
        monster : Datamodel.Monster = Datamodel.get_monster(message)
        user : Datamodel.UserRPGInfo = Datamodel.get_userRPGInfo(ctx.message.author.id)
        if user is None:
            await ctx.send('이 컨텐츠를 즐기기전에 회원가입부터 하십시오')
            return
        if monster is None:
            await ctx.send('선택한 몬스터는 없는 몬스터입니다')
            return

        await ctx.send(f"무서운 몬스터 {monster.name}이(가) 나타났다!")
        combat_text = ""
        embed = discord.Embed(title="전투 시작!", color=discord.Color.red())
        embed.add_field(name=f"{monster.name} 체력", value=f"{monster.now_hp} / {monster.hp}")
        embed.add_field(name=f"{user.name} 체력", value=f"{user.now_hp} / {user.hp}")
        embed.add_field(name="전투 텍스트", value=combat_text)
        embed_message = await ctx.send(embed=embed)
        def fight(who,target):
            text = ""
            target.now_hp -= who.attack
            text += f"{target.name}이 {who.name}에 의해 {who.attack}의 대미지를 받았다 \n"
            text += f"현재 {target.name}의 체력은 {target.now_hp}\n"
            who.now_hp -= target.attack
            text += f"{who.name}이 {target.name}에 의해 {target.attack}의 대미지를 받았다 \n"
            text += f"현재 {who.name}의 체력은 {who.now_hp}\n"
            return text

        async def editembed():
            embed.set_field_at(0, name=f"{monster.name} 체력", value=f"{monster.now_hp} / {monster.hp}")
            embed.set_field_at(1, name=f"{user.name} 체력", value=f"{user.now_hp} / {user.hp}")
            embed.set_field_at(2, name="전투 텍스트", value=combat_text)
            await embed_message.edit(embed=embed)

        while user.now_hp > 0 and monster.now_hp > 0:
            userSpeed = random.randint(user.speed,30)
            monsterSpeed = random.randint(monster.speed,30)
            if userSpeed>monsterSpeed:
                combat_text = fight(user,monster)
            else:
                combat_text = fight(monster, user)
            await asyncio.gather(
                editembed()
            )
            await asyncio.sleep(1)

        user.now_hp = clamp(user.now_hp,0,user.hp)
        monster.now_hp = clamp(monster.now_hp,0,999999)

        if user.now_hp == 0:
            await ctx.send(f"{user.name}은 {monster.name}에 의해 쓰러졌다.")
            return
        else:
            await ctx.send(f"{user.name}은 {monster.name}에게서 승리를 가져왔다!")




def clamp(n, min_value, max_value):
    return max(min(n, max_value), min_value)