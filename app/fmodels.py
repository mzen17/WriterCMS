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