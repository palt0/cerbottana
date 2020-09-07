# pylint: disable=too-few-public-methods

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from database import Database

db = Database.open()

Base = declarative_base(metadata=db.metadata)


class Badges(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True)
    userid = Column(String, index=True)
    image = Column(String, nullable=False)
    label = Column(String, nullable=False)


class EightBall(Base):
    __tablename__ = "eightball"
    id = Column(Integer, primary_key=True)
    answer = Column(String, nullable=False)


class Points(Base):
    __tablename__ = "points"
    __table_opts__ = (UniqueConstraint("userid", "date", sqlite_on_conflict="IGNORE"),)

    id = Column(Integer, primary_key=True)
    userid = Column(String, ForeignKey("users.userid"), nullable=False)
    roomid = Column(String, nullable=False)
    date = Column(String, nullable=False)
    tourpoints = Column(Integer, nullable=False)
    games = Column(Integer, nullable=False)
    first = Column(Integer, nullable=False)
    second = Column(Integer, nullable=False)
    third = Column(Integer, nullable=False)

    # user (many-to-one relationship)
    # Technically it isn't always guaranteed to have a corrisponding Users record, but
    # practically such exception is too rare to warrant a special behaviour.
    # It could occurr if a player that never joined a room before leaves a tournament
    # while the bot is offline and then the bot joins back before the tournament ends.
    # Such user also needs to gain points to impact leaderboards; furthermore, if they
    # subsequently join any room while the bot is online the inconsistency gets fixed.
    user = relationship("Users")

    @property
    def first_perc(self) -> float:
        return int(self.first / self.games * 100)

    @property
    def second_perc(self) -> float:
        return int(self.second / self.games * 100)

    @property
    def third_perc(self) -> float:
        return int(self.third / self.games * 100)


class Quotes(Base):
    __tablename__ = "quotes"
    __table_opts__ = (
        UniqueConstraint("message", "roomid", sqlite_on_conflict="IGNORE"),
    )

    id = Column(Integer, primary_key=True)
    message = Column(String, nullable=False)
    roomid = Column(String, nullable=False)
    author = Column(String)
    date = Column(String)


class Repeats(Base):
    __tablename__ = "repeats"
    __table_opts__ = (
        UniqueConstraint("message", "roomid", sqlite_on_conflict="REPLACE"),
    )

    id = Column(Integer, primary_key=True)
    message = Column(String, nullable=False)
    roomid = Column(String, nullable=False)
    delta_minutes = Column(Integer, nullable=False)
    initial_dt = Column(String, nullable=False)
    expire_dt = Column(String)


class Tokens(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String, index=True, nullable=False)
    room = Column(String)
    rank = Column(String, nullable=False)
    expiry = Column(String, nullable=False)


class Users(Base):
    __tablename__ = "users"
    __table_opts__ = (UniqueConstraint("userid", sqlite_on_conflict="IGNORE"),)

    id = Column(Integer, primary_key=True)
    userid = Column(String, nullable=False)
    username = Column(String)
    avatar = Column(String)
    description = Column(String)
    description_pending = Column(String, index=True)
