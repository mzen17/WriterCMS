from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database.connector import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    salt = Column(String)
    session = Column(String)
    session_exp = Column(Integer)

    buckets = relationship("Bucket", back_populates="owner")


class Bucket(Base):
    __tablename__ = "buckets"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="buckets")
    pages = relationship("Page", back_populates="owner")


class Page(Base):
    __tablename__ = "pages"

    id  = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)

    owner_id = Column(Integer, ForeignKey("buckets.id"))
    owner = relationship("Bucket", back_populates="pages")