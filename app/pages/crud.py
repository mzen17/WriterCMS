from app import fmodels
from sqlalchemy.orm import Session
import app.database.models as models

def create_page(data: fmodels.PageData, bucket_id: int, session: Session):
    if session:
        page = models.Page(title=data.title, description=data.content, owner_id=bucket_id)
        session.add(page)
        session.commit()
        session.refresh(page)
        return True
    return False


# Retrieves pages. Returns either a list of pages or none in case of non-existent user.
def get_pages(bucket_id: int, session: Session):
    if session:
        pages = session.query(models.Page).filter_by(owner_id = bucket_id).all()
        return pages
    return None


def get_page(bucket_id: int, page_id: int, session: Session):
    if session:
        target_page = session.query(models.Page).filter_by(owner_id=bucket_id).filter_by(id=page_id).first()
    return target_page


def update_page(data: fmodels.PageData, bucket_id: int, page_id: int, session: Session):
    if session:
        target_page = session.query(models.Page).filter_by(owner_id=bucket_id).filter_by(id=page_id).first()
        if target_page:
            target_page.title = data.title
            target_page.description = data.content
            session.commit()
            return True
    return False
