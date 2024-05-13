from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import fmodels
from app.users import functions
from app.database.connector import get_db
from app.pages import crud

router = APIRouter()


@router.post("/pages/list")
def list_pages(resp: fmodels.PageRequest, db: Session = Depends(get_db)):

    if functions.check_session(resp.username, resp.session, db):
       if functions.verify_bucket_ownership(resp.username, resp.bucketid, db):

            return{"resp":True, "pages":crud.get_pages(resp.bucketid, db)}

    return {"resp":False}


@router.post("/pages/get")
def pull_page(resp: fmodels.PageRequest, db: Session = Depends(get_db)):
    if functions.check_session(resp.username, resp.session, db):
       if functions.verify_bucket_view_access(resp.username, resp.bucketid, db):

            return {"resp":True,"page": crud.get_page(resp.bucketid, resp.pageid, db)}
    return {"resp":False}


@router.post("/editor/pages/update")
def update_page(resp: fmodels.PageData, db: Session = Depends(get_db)):

    if functions.check_session(resp.username, resp.session, db):
       if functions.verify_bucket_ownership(resp.username, resp.bucketid, db):

            return{"resp":True, "pages":crud.update_page(resp, resp.bucketid, resp.pageid, db)}

    return {"resp":False}


@router.post("/editor/pages/add")
def create_page(resp: fmodels.PageData, db: Session = Depends(get_db)):
    if functions.check_session(resp.username, resp.session, db):
       if functions.verify_bucket_ownership(resp.username, resp.bucketid, db):

            crud.create_page(resp, resp.bucketid, db)
            return {"resp": True}

    return {"resp":False}

@router.post("/editor/pages/delete")
def delete_page(resp: fmodels.PageRequest, db: Session = Depends(get_db)):
    if functions.check_session(resp.username, resp.session, db):
       if functions.verify_bucket_ownership(resp.username, resp.bucketid, db):

            crud.delete_page(resp, resp.bucketid, resp.pageid, db)
            return {"resp": True}

    return {"resp":False}
