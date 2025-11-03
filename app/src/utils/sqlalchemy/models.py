from sqlalchemy import Column, Integer, BigInteger, SmallInteger, String, Text
from sqlalchemy import Float, Numeric, Date, DateTime, Time, Boolean, LargeBinary, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False)
    is_active = Column(Boolean)

class Posts(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    published_at = Column(DateTime)
