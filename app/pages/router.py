from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import fmodels
from app.users import functions
from app.database.connector import get_db
from app.pages import crud

router = APIRouter()


@router.post("/pages/list")
def list_pages(resp: fmodels.PageRequest, db: Session = Depends(get_db)):

    page_list = crud.get_pages(resp.bucketid, db)
    page_list.sort(key=lambda x: x.id if x.id is not None else -1)
    page_list.sort(key=lambda x: x.porder if x.porder is not None else -1)

    #for page in page_list:
    #    print(page.id)

    if functions.check_session(resp.username, resp.session, db):
       if functions.verify_bucket_ownership(resp.username, resp.bucketid, db):
            return{"resp":True, "pages":page_list}
    
    elif functions.verify_bucket_view_access(resp.bucketid, db):
        return{"resp":True, "pages":page_list}

    return {"resp":False}


@router.post("/pages/get")
def pull_page(resp: fmodels.PageRequest, db: Session = Depends(get_db)):
    page = crud.get_page(resp.bucketid, resp.pageid, db)
    if page:
        user_valid = functions.check_session(resp.username, resp.session, db)
        user_owns = functions.verify_bucket_ownership(resp.username, resp.bucketid, db)

        access = page.public or (user_valid and user_owns)
        if access:
            page_list: list = crud.get_pages(resp.bucketid, db)

            page_list.sort(key=lambda x: x.id if x.id is not None else -1)
            page_list.sort(key=lambda x: x.porder if x.porder is not None else -1)

            index: int = 0
            while index < len(page_list):
                if page_list[index].id == page.id:
                    break

                index+=1
            
            nav = {}
            if index + 1 < len(page_list):
                nav["front"] = page_list[index + 1].id

            if index - 1 >= 0:
                nav["back"] = page_list[index - 1].id

            return {"resp":True,"page": crud.get_page(resp.bucketid, resp.pageid, db), "nav": nav}
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
