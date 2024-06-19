"""Main method for application. Routes that return HTML."""

import os

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import app.users.router as users
import app.buckets.router as buckets
import app.pages.router as pages

from app.database.connector import engine, get_db
from app.database import models

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Static Mount
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Routers for other modules
app.include_router(users.router)
app.include_router(buckets.router)
app.include_router(pages.router)

@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    """Main Home Page"""
    return templates.TemplateResponse("index.html",{"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_view(request: Request):
    """Login Page"""
    return templates.TemplateResponse("login.html",{"request": request})


@app.get("/buckets", response_class=HTMLResponse)
async def buckets_view(request: Request):
    """Return bucket view"""
    return templates.TemplateResponse("buckets.html",{"request": request})


@app.get("/bucket/{bid}", response_class=HTMLResponse)
async def sbucket_view(request: Request, bid: int):
    """Return a page view for a single particular bucket"""
    return templates.TemplateResponse("sbucket.html",{"request": request, "id":bid, "back_url":"/buckets"})


@app.get("/bucket/{bid}/page/{pid}", response_class=HTMLResponse)
async def pages_view(request: Request, bid: int, pid:int):
    """Return a page view for a particular page"""
    return templates.TemplateResponse("page.html",{"request": request, "id":bid, "pid":pid, "tinymce_url":os.environ["tinymce_url"], "back_url":"/buckets"})

# Public files
@app.get("/web", response_class=HTMLResponse)
async def global_home_view(request: Request):
    """Home Page (lists users)"""
    return templates.TemplateResponse("public_home.html",{"request": request})


@app.get("/web/{username}", response_class=HTMLResponse)
async def pub_buckets_view(request: Request, username: str):
    """Modified Buckets Page (lists users)"""
    return templates.TemplateResponse("public_buckets.html",{"request": request, "username":username})


@app.get("/web/{username}/bucket/{bucketid}", response_class=HTMLResponse)
async def pub_sbucket_view(request: Request, username: str, bucketid: int):
    """Modified Single Bucket Page to show contents"""
    return templates.TemplateResponse("public_bucket.html",{"request": request, "username":username, "bucketid":bucketid, "back_url":True})

from app.pages import crud
from app.users import functions

@app.get("/web/{username}/bucket/{bucketid}/page/{pageid}", response_class=HTMLResponse)
async def pub_page_view(request: Request, username: str, bucketid: int, pageid: int, db: Session = Depends(get_db)):
    """Modified Page view to show contents"""
    un = username
    sk = request.cookies.get('session_ck')

    if not sk:
        sk = ""

    pageHead = "This page is not public."
    pageCNT = "Please <a href='/login'>login</a> to view."

    backURL = ""
    tbcontentURL = f"/web/{username}/bucket/{bucketid}"
    frontURL = ""

    data = {
        "request": request, 
        "pg_title": pageHead,
        
        "tbURL": tbcontentURL,

        "pg_cnt": pageCNT,
        "pageid": pageid, 
    }
    page = crud.get_page(bucketid, pageid, db)
    if page:
        user_valid = functions.check_session(un, sk, db)
        user_owns = functions.verify_bucket_ownership(un, bucketid, db)

        access = page.public or (user_valid and user_owns)
        if access:
            page_list: list = crud.get_pages(bucketid, db)

            page_list.sort(key=lambda x: x.id if x.id is not None else -1)
            page_list.sort(key=lambda x: x.porder if x.porder is not None else -1)

            index: int = 0
            while index < len(page_list):
                if page_list[index].id == page.id:
                    break

                index+=1
            
            nav = {}
            if index + 1 < len(page_list):
                data["next"] =  f"/web/{username}/bucket/{bucketid}/page/{page_list[index + 1].id}"

            if index - 1 >= 0:
                data["back"] = f"/web/{username}/bucket/{bucketid}/page/{page_list[index - 1].id}"

            page = crud.get_page(bucketid, pageid, db)
            data["pg_cnt"] = page.description.replace("[@@#%]", "\"")
            data["pg_title"] = page.title

    return templates.TemplateResponse("public_page.html", data)
