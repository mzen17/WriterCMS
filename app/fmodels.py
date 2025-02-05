"""Models for POST requests. May also be used to type return dicts."""
from pydantic import BaseModel
from typing import Optional

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


class UserRequestSetting(BaseModel):
    """A request with session instead of password, for things like validating access"""
    old_username: str
    username: str
    session: str
    pfp: str
    bio: str

    dictionary: Optional[list[str]] = None
    theme: Optional[bool] = None



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
    bucket_id: int
    visibility: bool
    bucket_owner_id: Optional[int] = None
    
    description: Optional[str] = None
    background: Optional[str] = None
    banner: Optional[str] = None
    tags: Optional[str] = None


class PageRequest(BaseModel):
    """A request for a bucket. Has a bucketid included so that it can target a particular bucket"""
    username: str
    session: str
    bucketid: int
    pageid: int

class PageData(BaseModel):
    """A template request for page details. Useful in creation"""
    username: str
    session: str
    title: str
    content: str
    bucketid: int
    pageid: int
    visibility: bool
    porder: Optional[int] = None