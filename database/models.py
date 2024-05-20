from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from datetime import datetime

from .database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    status = Column(String, default="alive")
    status_updated_at = Column(DateTime, default=datetime.now())


class StageOne(Base):
    __tablename__ = "stage_one"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())

    user = Column(ForeignKey("user.id"))


class StageTwo(Base):
    __tablename__ = "stage_two"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())

    user = Column(ForeignKey("user.id"))


class StageThree(Base):
    __tablename__ = "stage_three"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())

    user = Column(ForeignKey("user.id"))
