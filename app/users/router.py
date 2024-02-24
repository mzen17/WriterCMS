from fastapi import APIRouter, Depends
from app import fmodels
from sqlalchemy.orm import Session

from app.database import crud
from app.database.connector import get_db
from app.passwd import hash_password, verify_password, generate_hash


router = APIRouter()


@router.post("/users/create")
def create_user(user: fmodels.Credentials, db: Session = Depends(get_db)):
    hash_pass = hash_password(user.password)    
    updated_user = fmodels.SaltedUser(username=user.username, password=hash_pass[0], salt=hash_pass[1])
    return {"resp":crud.create_user(updated_user, db)}


@router.post("/users/authenticate")
def login(creds: fmodels.Credentials, db: Session = Depends(get_db)):
    salted_user = crud.get_user_data(creds.username, db)
    if salted_user:
        if verify_password(salted_user.password, salted_user.salt, creds.password):
            return {"resp":True, "session_ck":generate_hash()}
    return {"resp":False}
