from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import fmodels
from app.users import functions

from app.database.connector import get_db


router = APIRouter()


@router.post("/users/create")
def create_user(user: fmodels.Credentials, db: Session = Depends(get_db)):
    return {"resp":functions.create_user(user.username, user.password, db)}


@router.post("/users/authenticate")
def login(creds: fmodels.Credentials, db: Session = Depends(get_db)):
    submit = functions.check_password(creds.username, creds.password, db)

    if submit[0]:
        return {"resp":True, "session_ck":submit[1][0], "exp":submit[1][1]}

    return {"resp":False}


@router.post("/users/session_validate")
def validate_session(creds: fmodels.UserRequest, db: Session = Depends(get_db)):
    return {"resp":functions.check_session(creds.username, creds.session, db)}

