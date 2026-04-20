from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(BigInteger, primary_key=True)
    user_telegram_id = Column(BigInteger, nullable=False)
    message_text = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    is_sent = Column(Boolean, default=False)
