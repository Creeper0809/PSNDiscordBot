import discord
from dotenv import load_dotenv
from sqlalchemy import create_engine, Integer, Column, String, Date, or_, and_, ForeignKey, union_all, Float
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

import Datamodel

Base = declarative_base()
rarityColor = {
    "노말" : "\n",
    "언커먼" : "yaml\n",
    "에픽" : "md\n",
    "레전드리" : "fix\n",
    "신화" : "diff\n"
}
class Monster(Base):
    __tablename__ = 'Monster'
    id = Column(Integer,primary_key=True)
    name = Column(String)
    level= Column(Integer)
    dropPWN = Column(Integer)
    hp = Column(Integer)
    now_hp = Column(Integer)
    attack = Column(Integer)
    defense = Column(Integer)
    speed = Column(Integer)
    dungeon = Column(String,ForeignKey('Dungeon_info.name'))
    dungeon_name = relationship('Dungeon_info', back_populates='spawn_pointsDB')
    droptablesDB = relationship('Droptable', back_populates='monster_name')
    droptable = list()


    def copy(self):
        return Monster(name = self.name,
                       level = self.level,
                       hp = self.hp,
                       dropPwn = self.dropPWN,
                       now_hp = self.now_hp,
                       attack = self.attack,
                       defense = self.defense,
                       speed = self.speed,
                       droptable = self.droptable
                       )

    def getDiscription(self):
        spac = ""
        spac += ":heart: 체력:%20s\n" % f"{self.now_hp}"
        spac += ":crossed_swords: 공격력:%20s\n" % f"{int(self.attack * 0.9)}~{int(self.attack * 1.1)}"
        spac += ":magic_wand: 마법공격력:%20s\n" % "0~0"
        spac += ":shield: 방어력:%20s\n" % f"{self.defense}"
        spac += ":boot: 민첩도:%20s" % f"{self.speed}"

        embed = discord.Embed()
        embed.set_author(name=f"무서운 몬스터 {self.name}이(가) 나타났다!")
        embed.add_field(name=f"{self.name}의 정보", value="", inline=False)
        embed.add_field(name="레벨", value=f"{self.level}", inline=False)
        embed.add_field(name="스펙", value=spac, inline=False)

        return embed

class Droptable(Base):
    __tablename__ = 'Droptable'
    id = Column(Integer,primary_key=True)
    drop_monster = Column(Integer,ForeignKey('Monster.id'))
    monster_name = relationship('Monster', back_populates='droptablesDB')
    probability = Column(Float)
    item_id = Column(Integer)

class UserRPGInfo(Base):
    __tablename__ = 'UserRPGInfo'
    id = Column(String,primary_key=True)
    name = Column(String,default="무명")
    level = Column(Integer, default=1)
    accumulated_exp= Column(Integer, default=0)
    hp = Column(Integer, default=30)
    now_hp = Column(Integer, default=30)
    attack = Column(Integer,default=8)
    accuracy = Column(Integer,default=3)
    defense = Column(Integer, default=0)
    speed = Column(Integer, default=10)
    stats_remaining = Column(Integer, default=1)
    Str = Column(Integer, default=0)
    Int = Column(Integer, default=0)

    ability = dict()

    def getDiscription(self):
        spac = ""
        spac += ":heart: 체력:%20s\n" % f"{self.now_hp}/{self.hp}"
        spac += ":crossed_swords: 공격력:%20s\n" % f"{int(self.attack * 0.9)}~{int(self.attack * 1.1)}"
        spac += ":magic_wand: 마법공격력:%20s\n" % "0~0"
        spac += ":shield: 방어력:%20s\n" % f"{self.defense}"
        spac += ":boot: 민첩도:%20s" % f"{self.speed}"

        embed = discord.Embed()
        embed.set_author(name=f"{self.name}의 정보")
        embed.add_field(name="레벨", value=f"{self.level}", inline=False)
        embed.add_field(name="EXP", value="", inline=True)
        embed.add_field(name="스펙", value=spac, inline=False)
        embed.add_field(name="-" * 30, value="", inline=True)
        embed.add_field(name="남은 스탯", value=f"{self.stats_remaining}", inline=False)
        return embed


    def get_inv_info(self):
        items = ""
        value = ""
        embed = discord.Embed(title=f"{self.name}의 인벤토리")
        tables = get_userinv(self.id)
        for item_id in tables:
            item = getItem(item_id.item_code)
            items += item.name+'\n'
            value += f"{item_id.quantity}"
            if item_id.is_equiped == 1:
                value += f" ({item_id.equip_pos}에 장착중)"
            value+="\n"
        embed.add_field(name="아이템",value=items.rstrip())
        embed.add_field(name="개수", value=value.rstrip())
        return embed
    def get_equip_item(self):
        table = get_userinv(self.id)
        equip_items = list()
        for i in table:
            if i.is_equiped == 1:
                equip_items.append(i)
        return equip_items


    def get_equip_item_info(self):
        items = ""
        value = ""
        equip_items = self.get_equip_item()
        embed = discord.Embed(title=f"{self.name}의 장착 장비")
        for item_id in equip_items:
            item = getItem(item_id.item_code)
            items += item.name+'\n'
            value += f"{item_id.equip_pos}\n"
        embed.add_field(name="아이템",value=items.rstrip())
        embed.add_field(name="장착 위치", value=value.rstrip())
        return embed

    def hasItem(self,item_code,equiped = 0):
        tables = get_userinv(self.id)
        for item_id in tables:
            if item_id.item_code == item_code and equiped == item_id.is_equiped:
                return True
        return False


class Consumable_item(Base):

    __tablename__ = "consumable_item"
    id = Column(Integer,primary_key=True)
    name = Column(String)
    ability = Column(String)
    dungeon_pos= Column(String)

    def use(self,user : UserRPGInfo):
        print(f"{self.name} 소모품 사용 됨")


class Equipment_item(Base):
    __tablename__ = "equipment_item"
    id = Column(Integer,primary_key=True)
    name = Column(String)
    description= Column(String)
    ability = Column(String)
    attack = Column(Integer)
    hp = Column(Integer)
    ap_attack = Column(Integer)
    defense = Column(Integer)
    equip_position = Column(String)
    rarity = Column(String)
    dungeon_pos = Column(String)

    def use(self,user:UserRPGInfo):
        Session = sessionmaker(bind=Datamodel.connection_pool)
        session = Session()
        equiped_item = session.query(UserInv).filter(and_(UserInv.equip_pos == self.equip_position,UserInv.is_equiped == 1)).first()
        text = f"{self.name} 장착 완료"

        if equiped_item is not None:
            item = getItem(equiped_item.item_code)
            user.attack -= item.attack
            user.hp -= item.hp
            user.now_hp -= item.hp
            user.defense -= item.defense
            text = f"{item.name} -> {self.name} 교환 완료"
            session.delete(equiped_item)
            add_item_to_inventory(user.id,item.id,1)
            session.commit()

        user.attack += self.attack
        user.hp += self.hp
        user.now_hp += self.hp
        user.defense += self.defense
        add_item_to_inventory(user.id, self.id, -1)
        add_item_to_inventory(user.id, self.id, 1,self.equip_position,1)
        update_datamodel(user)
        session.commit()
        session.close()
        return text


    def getDiscription(self):
        embed = discord.Embed(title=f"{self.name}의 정보",
                              description=self.description)
        rare = "```"+rarityColor[self.rarity]+self.rarity+"\n```"
        embed.add_field(name="등급",value=rare)
        embed.add_field(name="장착위치",value=self.equip_position)
        embed.add_field(name="능력",value=self.ability,inline=False)
        spac = ""
        if self.hp > 0:
            spac += ":heart: 체력: +%20s\n" % f"{self.hp}"
        if self.attack > 0:
            spac += ":crossed_swords: 공격력: +%20s\n" % f"{self.attack}"
        if self.ap_attack > 0:
            spac += ":magic_wand: 마법공격력: +%20s\n" % f"{self.ap_attack}"
        if self.defense > 0:
            spac += ":shield: 방어력: +%20s\n" % f"{self.defense}"
        embed.add_field(name="스펙",value=spac,inline=False)
        return embed

class Experience_table(Base):
    __tablename__ = 'Experience_table'
    level = Column(Integer,primary_key=True)
    accumulated_experience = Column(Integer)
    required_experience = Column(Integer)


class Dungeon_info(Base):
    __tablename__ = 'Dungeon_info'
    name = Column(String,primary_key=True)
    min_level = Column(Integer)
    description = Column(String)
    spawn_pointsDB = relationship('Monster', back_populates='dungeon_name')
    spawn_points = list()

class UserInv(Base):
    __tablename__ = 'UserInv'
    id = Column(Integer,primary_key=True)
    discord_id = Column(String)
    item_code = Column(Integer)
    quantity = Column(Integer)
    equip_pos = Column(String)
    is_equiped= Column(Integer)



def get_userinv(id):
    Session = sessionmaker(bind=Datamodel.connection_pool)
    session = Session()
    tables = session.query(UserInv).filter(UserInv.discord_id == id).all()
    session.close()
    return tables

def get_monster(name):
    Session = sessionmaker(bind=Datamodel.connection_pool)
    session = Session()
    result = session.query(Monster).filter(Monster.name == name).first()
    if result is None:
        session.close()
        return None
    result.droptable = result.droptablesDB
    session.close()
    return result


def get_items_bydungeon(name):
    Session = sessionmaker(bind=Datamodel.connection_pool)
    session = Session()
    itemList = list()
    itemList += session.query(Consumable_item).filter(Consumable_item.dungeon_pos == name).all()
    itemList += session.query(Equipment_item).filter(Equipment_item.dungeon_pos == name).all()

    return itemList


def get_experimentTable(user_experiment : UserRPGInfo):
    Session = sessionmaker(bind=Datamodel.connection_pool)
    session = Session()
    a = (session.query(Experience_table)
         .filter(Experience_table.accumulated_experience <= user_experiment.accumulated_exp)
         .order_by(Experience_table.level.desc())
         .first())
    session.close()
    return a

def get_dungeon(name):
    Session = sessionmaker(bind=Datamodel.connection_pool)
    session = Session()
    result = session.query(Dungeon_info).filter(Dungeon_info.name == name).first()
    if result is None:
        session.close()
        return None
    result.spawn_points = result.spawn_pointsDB
    session.close()
    return result


def get_userRPGInfo(id):
    Session = sessionmaker(bind=Datamodel.connection_pool)
    session = Session()
    results = session.query(UserRPGInfo).filter(UserRPGInfo.id == id).all()
    session.close()
    if len(results) == 0:
        return None
    return results[0]


def add_item_to_inventory(user_id, item_code, quantity,equip_pos = "",isequiped = 0):
    Session = sessionmaker(bind=Datamodel.connection_pool)
    session = Session()
    user = session.query(UserRPGInfo).get(user_id)
    if user is None:
        return False
    inventory_item = session.query(UserInv).filter_by(discord_id=user_id, item_code=item_code,
                                                      is_equiped=isequiped).first()

    if inventory_item is None:
        inventory_item = UserInv(item_code=item_code, quantity=quantity, discord_id=user_id, equip_pos=equip_pos,
                                 is_equiped=isequiped)
        print(inventory_item.item_code, inventory_item.is_equiped,"1")
        session.add(inventory_item)
    else:
        print(inventory_item.item_code, inventory_item.is_equiped,"2")
        inventory_item.quantity += quantity
        if inventory_item.quantity <= 0:
            session.delete(inventory_item)
    session.commit()
    return True


def update_datamodel(user):
    Session = sessionmaker(bind=Datamodel.connection_pool)
    session = Session()
    existing_data = session.query(type(user)).get(user.id)
    for key, value in user.__dict__.items():
        if key != '_sa_instance_state':
            setattr(existing_data, key, value)
    session.commit()
    session.close()

def getItem(item_id):
    Session = sessionmaker(bind=Datamodel.connection_pool)
    session = Session()
    if isinstance(item_id,int):
        consumable_item = session.query(Consumable_item).filter(Consumable_item.id == item_id).first()
        equipment_item = session.query(Equipment_item).filter(Equipment_item.id==item_id).first()
    else:
        consumable_item = session.query(Consumable_item).filter(Consumable_item.name==item_id).first()
        equipment_item = session.query(Equipment_item).filter(Equipment_item.name==item_id).first()
    if consumable_item is None and equipment_item is None:
        return None
    elif consumable_item is None:
        item = equipment_item
    else:
        item = consumable_item
    return item

