import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, Integer, Column, String, Date, or_, and_, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class User(Base):
    __tablename__ = 'User'
    id = Column(String, primary_key=True)
    discord_name = Column(String)
    PWN = Column(Integer, default=0)
    baekjoon_id = Column(String,default="")
    attendance_check = Column(Date,default="2020-04-21")


class Monster(Base):
    __tablename__ = 'Monster'
    id = Column(Integer,primary_key=True)
    name = Column(String)
    hp = Column(Integer)
    now_hp = Column(Integer)
    maxattack = Column(Integer)
    minattack = Column(Integer)
    defense = Column(Integer)
    speed = Column(Integer)
    dungeon = Column(String,ForeignKey('Dungeon_info.name'))
    dungeon_name = relationship('Dungeon_info', back_populates='spawn_points')

class UserRPGInfo(Base):
    __tablename__ = 'UserRPGInfo'
    id = Column(String,primary_key=True)
    name = Column(String,default="무명")
    level = Column(Integer, default=1)
    accumulated_exp= Column(Integer, default=0)
    hp = Column(Integer, default=30)
    now_hp = Column(Integer, default=30)
    maxattack = Column(Integer,default=8)
    minattack = Column(Integer,default=3)
    defense = Column(Integer, default=0)
    speed = Column(Integer, default=10)
    stats_remaining = Column(Integer, default=1)
    Str = Column(Integer, default=0)
    Int = Column(Integer, default=0)

class Experience_table(Base):
    __tablename__ = 'Experience_table'
    level = Column(Integer,primary_key=True)
    accumulated_experience = Column(Integer)
    required_experience = Column(Integer)


class Dungeon_info(Base):
    __tablename__ = 'Dungeon_info'
    name = Column(String,primary_key=True)
    min_level =  Column(Integer)
    description = Column(String)
    spawn_points = relationship('Monster', back_populates='dungeon_name')

def makeDB():
    global connection_pool
    load_dotenv()
    db_url = f'mysql+pymysql://{os.environ.get("USER")}:{os.environ.get("PASSWORD")}@{os.environ.get("HOST")}' \
             f':{os.environ.get("PORT")}/{os.environ.get("DATABASE")}'
    connection_pool = create_engine(db_url, pool_size=5, max_overflow=5, echo=True)

def get_user(id):
    Session = sessionmaker(bind=connection_pool)
    session = Session()
    results = session.query(User).filter(User.id == id).all()
    session.close()
    if len(results) == 0:
        return None
    return results[0]

def get_experimentTable(user_experiment : UserRPGInfo):
    print(user_experiment.accumulated_exp)
    Session = sessionmaker(bind=connection_pool)
    session = Session()
    a = (session.query(Experience_table)
         .filter(Experience_table.accumulated_experience <= user_experiment.accumulated_exp)
         .order_by(Experience_table.level.desc())
         .first())
    session.close()
    return a

def get_dungeon(name):
    Session = sessionmaker(bind=connection_pool)
    session = Session()
    result = session.query(Dungeon_info).filter(Dungeon_info.name == name).first()
    if result is None:
        session.close()
        return None
    monsters = result.spawn_points
    session.close()
    return (result,monsters)


def get_userRPGInfo(id):
    Session = sessionmaker(bind=connection_pool)
    session = Session()
    results = session.query(UserRPGInfo).filter(UserRPGInfo.id == id).all()
    session.close()
    if len(results) == 0:
        return None
    return results[0]

def add_user(id,discord_name):
    Session = sessionmaker(bind=connection_pool)
    session = Session()
    newData = User(id = id,discord_name = discord_name)
    session.add(newData)
    newinfoData = UserRPGInfo(discord_id = id)
    session.add(newinfoData)
    session.commit()
    session.close()

def update_user(id,discord_name,pwn,baekjoon,attendance_check):
    Session = sessionmaker(bind=connection_pool)
    session = Session()
    session.query(User).filter(User.id == id).update({'discord_name': discord_name,
                                                      'PWN':pwn,
                                                      'baekjoon_id':baekjoon,
                                                      'attendance_check':attendance_check
                                                      })
    session.commit()
    session.close()


def update_userByUserClass(user,baekjoonid):
    Session = sessionmaker(bind=connection_pool)
    session = Session()
    session.query(User).filter(User.id == user.id).update({'baekjoon_id': baekjoonid})
    session.commit()
    session.close()

def update_PWN(id,amount : int):
    Session = sessionmaker(bind=connection_pool)
    session = Session()
    a = session.query(User).filter(User.id == id).first()
    a.PWN += amount
    session.commit()
    session.close()

def update_datamodel(user):
    Session = sessionmaker(bind=connection_pool)
    session = Session()
    existing_data = session.query(type(user)).get(user.id)
    for key, value in user.__dict__.items():
        if key != '_sa_instance_state':
            setattr(existing_data, key, value)
    session.commit()
    session.close()

def update_gameInfo(id,health):
    Session = sessionmaker(bind=connection_pool)
    session = Session()
    session.query(UserRPGInfo).filter(UserRPGInfo.discord_id == id).update({'now_hp':health})


def get_monster(name):
    Session = sessionmaker(bind=connection_pool)
    session = Session()
    results = session.query(Monster).filter(Monster.name == name).all()
    session.close()
    if len(results) == 0:
        return None
    return results[0]