from typing import List, Optional

from app import fmodels
from sqlalchemy.orm import Session
import app.database.models as models

# Creates a bucket
def create_bucket(bk: fmodels.BucketData, session: Session):
    if session:
        user = session.query(models.User).filter_by(username=bk.username).first()
        if user:
            bucket = models.Bucket(name=bk.bucket_name, owner_id=user.id)
            if bk.bucket_id1:
                bucket.bucket_owner_id = bk.bucket_id1
            
            session.add(bucket)
            session.commit()
            session.refresh(user)

            return True
    return False


# Retrieves a user. Returns either a user or none in case of non-existent user.
def get_buckets(username: str, session: Session) -> Optional[List[models.Bucket]]:
    if session:
        user = session.query(models.User).filter_by(username=username).first()
        if user:
            buckets = session.query(models.Bucket).filter_by(owner_id=user.id).all()
            return buckets
    return None


# Retrieves a user. Returns either a user or none in case of non-existent user.
def get_prim_buckets(username: str, session: Session) -> Optional[List[models.Bucket]]:
    if session:
        user = session.query(models.User).filter_by(username=username).first()
        if user:
            buckets = session.query(models.Bucket).filter_by(owner_id=user.id).filter_by(bucket_owner_id=None).all()
            return buckets
    return None


def get_bucket(bucket_id: int, session: Session) -> models.Bucket:
    if session:
        bucket = session.query(models.Bucket).filter_by(id=bucket_id).first()
        return bucket
    return None

def get_bucket_buckets(bucket_id: int, session: Session) -> list[models.Bucket]:
    if session:
        buckets = session.query(models.Bucket).filter_by(bucket_owner_id=bucket_id).all()
        return buckets
    return []

def get_bucket_pages(bucket_id: int, session: Session) -> list[dict[str, int]]:
    if session:
        pages = session.query(models.Page).filter_by(owner_id=bucket_id).all()
        page_summary_list = []

        for page in pages:
            page_summary = {}
            page_summary["name"] = page.title
            page_summary["id"] = page.id
            page_summary_list.append(page_summary)
        return page_summary_list
    return []

# Faq a bucket up in the database
def faq_bucket(bucket_id: int):
    pass
