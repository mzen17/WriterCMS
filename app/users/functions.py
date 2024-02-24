import time
from sqlalchemy.orm import Session

import app.database.crud

def create_session_token(username: str, db: Session):
    hash_token = generate_hash()
    exp_time = time.time() + 2592000