import os

from dotenv import load_dotenv
from sqlalchemy import String, Integer, Date, Column, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from RPGDatamodel import UserRPGInfo
Base = declarative_base()

def makeDB():
    global connection_pool
    load_dotenv()
    db_url = f'mysql+pymysql://{os.environ.get("USER")}:{os.environ.get("PASSWORD")}@{os.environ.get("HOST")}' \
             f':{os.environ.get("PORT")}/{os.environ.get("DATABASE")}'
    connection_pool = create_engine(db_url, pool_size=5, max_overflow=5, echo=True)


class User(Base):
    __tablename__ = 'User'
    id = Column(String, primary_key=True)
    discord_name = Column(String)
    PWN = Column(Integer, default=0)
    baekjoon_id = Column(String,default="")
    attendance_check = Column(Date,default="2020-04-21")



def update_userByUserClass(user, baekjoonid):
    Session = sessionmaker(bind=connection_pool)
    session = Session()
    session.query(User).filter(User.id == user.id).update({'baekjoon_id': baekjoonid})
    session.commit()
    session.close()

def get_user(id):
    Session = sessionmaker(bind=connection_pool)
    session = Session()
    results = session.query(User).filter(User.id == id).all()
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