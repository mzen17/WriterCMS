import time
from sqlalchemy.orm import Session

import app.users.crud as user_crud
import app.buckets.crud as bucket_crud

from app.passwd import hash_password, verify_password, generate_hash
from app import fmodels


def create_user(username: str, password: str, db: Session) -> bool:
    hash_pass = hash_password(password)
    updated_user = fmodels.SaltedUser(username=username, password=hash_pass[0], salt=hash_pass[1])

    return user_crud.create_user(updated_user, db)


# Create session token to database
def create_session_token(username: str, db: Session) -> (str, int):
    hash_token = generate_hash()
    exp_time = time.time() + 2592000

    user = user_crud.get_user_data(username, db)
    if user:
        user.session = hash_token
        user.session_exp = exp_time

        user_crud.update_user(user, db)
    
    return hash_token, exp_time



def check_password(username: str, password: str, db: Session) -> (bool, (str, int)):
    salted_user = user_crud.get_user_data(username, db)
    if salted_user:

        # Verify password.
        if verify_password(salted_user.password, salted_user.salt, password):
            return True, create_session_token(username, db)
    
    return False, None



# Ensure session is valid.
# session_key(s) to check, ensure exp_time is valid.
def check_session(username: str, session_ck: str, db: Session) -> bool:
    user = user_crud.get_user_data(username, db)
    if user:
        if session_ck == user.session and user.session_exp > time.time():
            return True
    return False


# Get user id from name
def get_id(username: str, db: Session) -> int:
    user = user_crud.get_user_data(username, db)
    return user.id
    

def verify_bucket_ownership(username: str, bucket_id: int, db: Session):
    owner = get_id(username, db)
    bucket = bucket_crud.get_bucket(bucket_id, db)

    if bucket:
        if owner == bucket.owner_id:
            return True
    return False


def verify_bucket_view_access(username: str, bucket_id: int, db: Session):
    owner = get_id(username, db)
    bucket = bucket_crud.get_bucket(bucket_id, db)

    if bucket:
        if bucket.visibility:
            return True

        if owner == bucket.owner_id:
            return True
    return False

