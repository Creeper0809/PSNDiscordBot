import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Integer, Column, String, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


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

def get_userRPGInfo(id):
    Session = sessionmaker(bind=connection_pool)
    session = Session()
    results = session.query(UserRPGInfo).filter(UserRPGInfo.discord_id == id).all()
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


def get_monster(name):
    Session = sessionmaker(bind=connection_pool)
    session = Session()
    results = session.query(Monster).filter(Monster.name == name).all()
    session.close()
    if len(results) == 0:
        return None
    return results[0]


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
    attack = Column(Integer)
    defense = Column(Integer)
    speed = Column(Integer)

class UserRPGInfo(Base):
    __tablename__ = 'UserRPGInfo'
    id = Column(Integer,primary_key=True)
    discord_id = Column(String)
    name = Column(String,default="무명")
    level = Column(Integer, default=1)
    hp = Column(Integer, default=30)
    now_hp = Column(Integer, default=30)
    attack = Column(Integer, default=5)
    defense = Column(Integer, default=0)
    speed = Column(Integer, default=10)

def update_userByUserClass(user,baekjoonid):
    Session = sessionmaker(bind=connection_pool)
    session = Session()
    session.query(User).filter(User.id == user.id).update({'baekjoon_id': baekjoonid})
    session.commit()
    session.close()