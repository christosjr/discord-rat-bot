import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base

db_url = os.getenv("DATABASE_URL", "sqlite:///players.db")
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    print(f"📘 Database initialized using: {db_url}")
