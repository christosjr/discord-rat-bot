from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Player(Base):
    __tablename__ = "players"
    discord_id = Column(Integer, primary_key=True)
    name = Column(String)
    emoji = Column(String)
    color = Column(String)
    hp = Column(Integer)
    stamina = Column(Integer)
    magicka = Column(Integer)
    traits = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
