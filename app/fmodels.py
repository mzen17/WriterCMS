"""Models for POST requests. May also be used to type return dicts."""
from pydantic import BaseModel

class Credentials(BaseModel):
    """Standard username password login request"""
    username: str
    password: str


class SaltedUser(BaseModel):
    """Username and password with a salt. Usually something pulled out of database."""
    username: str
    password: str
    salt: str


class UserRequest(BaseModel):
    """A request with session instead of password, for things like validating access"""
    username: str
    session: str


class BucketRequest(BaseModel):
    """A request for a bucket. Has a bucketid included so that it can target a particular bucket"""
    username: str
    session: str
    bucketid: int


class BucketData(BaseModel):
    """A template request for bucket details. Useful in creation"""
    username: str
    session: str
    bucket_name: str


class PageData(BaseModel):
    """A template request for page details. Useful in creation"""
    username: str
    session: str
    title: str
    content: str