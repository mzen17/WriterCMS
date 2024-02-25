# Models with forms of POST requests.
from pydantic import BaseModel


# Standard username password request.
class Credentials(BaseModel):
    username: str
    password: str


class SaltedUser(BaseModel):
    username: str
    password: str
    salt: str


class UserRequest(BaseModel):
    username: str
    session: str


class BucketRequest(BaseModel):
    username: str
    session: str
    bucketid: int


class BucketData(BaseModel):
    username: str
    session: str
    bucket_name: str


class PageData(BaseModel):
    username: str
    session: str
    title: str
    content: str