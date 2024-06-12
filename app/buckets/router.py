from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import fmodels
from app.users.functions import check_session, get_id, verify_bucket_ownership
from app.database.connector import get_db
from app.buckets import crud

router = APIRouter()

# Public API
@router.post("/buckets/list")
def list_buckets(user: fmodels.UserRequest, db: Session = Depends(get_db)):
    if check_session(user.username, user.session, db):
        return {"resp":True, "buckets":crud.get_prim_buckets(user.username, db)}
    else:
        buckets = []
        bucket_list = crud.get_prim_buckets(user.username, db)
        if bucket_list:
            for bucket in bucket_list:
                if bucket.visibility:
                    buckets.append(bucket)
        return {"resp":True, "buckets":buckets}


@router.post("/buckets/get")
def get_buckets(bk: fmodels.BucketRequest, db: Session = Depends(get_db)):
    tb = crud.get_bucket(bk.bucketid, db)

    buckets = crud.get_bucket_buckets(bk.bucketid, db)
    pages = crud.get_bucket_pages(bk.bucketid, db)

    pages.sort(key=lambda x: x["id"])
    pages.sort(key=lambda x: x["order"])

    # If the bucket is public
    if tb and tb.visibility:
        return {"resp":True, "bucket":tb, "buckets":buckets,"pages":pages}

    # Otherwise run through and check
    if check_session(bk.username, bk.session, db):

        # Check bucket ownership
        if tb and (tb.owner_id == get_id(bk.username, db)):
            return {"resp":True, "bucket":tb, "buckets":buckets,"pages":pages}

    return {"resp":False}


# Editor-only commands (Run verification process)
@router.post("/editor/buckets/create")
def create_bucket(bucket: fmodels.BucketData, db: Session = Depends(get_db)):
    if check_session(bucket.username, bucket.session, db):
        return {"resp":crud.create_bucket(bucket, db)}
    return {"resp":False}



@router.post("/editor/buckets/update")
def update_bucket(resp: fmodels.BucketData, db: Session = Depends(get_db)):

    if check_session(resp.username, resp.session, db):
       if verify_bucket_ownership(resp.username, resp.bucket_id, db):

            return{"resp":True, "pages":crud.update_bucket(resp, db)}
    return {"resp":False}


@router.post("/editor/buckets/delete")
def delete_bucket(resp: fmodels.BucketRequest,  db: Session = Depends(get_db)):
    if check_session(resp.username, resp.session, db):
       if verify_bucket_ownership(resp.username, resp.bucketid, db):

        return {"resp": crud.faq_bucket(resp.bucketid, db)}
    return {"resp": False}
