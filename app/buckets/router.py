from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import fmodels
from app.users.functions import check_session, get_id
from app.database.connector import get_db
from app.buckets import crud

router = APIRouter()


@router.post("/buckets/list")
def list_buckets(user: fmodels.UserRequest, db: Session = Depends(get_db)):
    if check_session(user.username, user.session, db):
        return {"resp":True, "buckets":crud.get_buckets(user.username, db)}
    return {"resp":False}


@router.post("/buckets/create")
def create_bucket(bucket: fmodels.BucketData, db: Session = Depends(get_db)):
    return {"resp":crud.create_bucket(bucket, db)}


@router.post("/buckets/get")
def list_buckets(bk: fmodels.BucketRequest, db: Session = Depends(get_db)):
    if check_session(bk.username, bk.session, db):
        tb = crud.get_bucket(bk.bucketid, db)

        if tb.owner_id == get_id(bk.username, db):
            return {"resp":True, "bucket":tb}
    return {"resp":False}


@router.post("/buckets/delete")
def delete_bucket(bucket: fmodels.BucketRequest,  db: Session = Depends(get_db)):
    pass
