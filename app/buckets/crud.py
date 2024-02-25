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


def get_bucket(bucket_id: int, session: Session) -> models.Bucket:
    if session:
        bucket = session.query(models.Bucket).filter_by(id=bucket_id).first()
        return bucket
    return None


# Faq a bucket up in the database
def faq_bucket(bucket_id: int):
    pass
