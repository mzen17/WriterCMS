from sqlalchemy import Column, ForeignKey, Integer, String, TEXT, Boolean
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
    bucket_owner_id = Column(Integer, ForeignKey("buckets.id"), nullable=True)
    visibility = Column(Boolean, unique=False, default=True, nullable=False)

    owner = relationship("User", back_populates="buckets")
    parent_bucket = relationship("Bucket", remote_side=[id])
    pages = relationship("Page", back_populates="owner")



class Page(Base):
    __tablename__ = "pages"

    id  = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(TEXT, index=False)

    owner_id = Column(Integer, ForeignKey("buckets.id"))
    owner = relationship("Bucket", back_populates="pages")