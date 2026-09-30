from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

from .setting import setting

engine = create_engine(setting.SQLALCHEMY_POSTGRES_DATABASE_URL)

class Base(DeclarativeBase):
    pass

def get_db():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()