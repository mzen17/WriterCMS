# Models with forms of POST requests.
from pydantic import BaseModel

class Credentials(BaseModel):
    user: str
    passwd: str