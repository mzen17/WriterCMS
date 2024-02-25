from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import fmodels
from app.users import functions
from app.database.connector import get_db
from app.pages import crud

router = APIRouter()


@router.post("/bucket/{bid}/pages")
def list_pages(resp: fmodels.UserRequest, bid: str, db: Session = Depends(get_db)):

    if functions.check_session(resp.username, resp.session, db):
       if functions.verify_bucket_ownership(resp.username, bid, db):

            return{"resp":True, "pages":crud.get_pages(bid, db)}

    return {"resp":False}


@router.post("/bucket/{bid}/get/{pid}")
def pull_page(resp: fmodels.UserRequest, bid: str, pid: str, db: Session = Depends(get_db)):
    if functions.check_session(resp.username, resp.session, db):
       if functions.verify_bucket_ownership(resp.username, bid, db):

            return {"resp":True,"page": crud.get_page(bid, pid, db)}
    return {"resp":False}


@router.post("/bucket/{bid}/update/{pid}")
def update(resp: fmodels.PageData, bid: str, pid: str, db: Session = Depends(get_db)):
    if functions.check_session(resp.username, resp.session, db):
       if functions.verify_bucket_ownership(resp.username, bid, db):

            return{"resp":True, "pages":crud.update_page(resp, bid, pid, db)}

    return {"resp":False}


@router.post("/bucket/{bid}/addpage")
def create_page(resp: fmodels.PageData, bid: str, db: Session = Depends(get_db)):
    if functions.check_session(resp.username, resp.session, db):
       if functions.verify_bucket_ownership(resp.username, bid, db):

            crud.create_page(resp, bid, db)
            return {"resp": True}

    return {"resp":False}

@router.post("/bucket/{bid}/delete")
def delete_page(db: Session = Depends(get_db)):
    pass
