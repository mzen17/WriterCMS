"""Main method for application. Routes that return HTML."""

import os
import shutil

from fastapi import FastAPI, Request, Depends, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import app.users.router as users
import app.buckets.router as buckets
import app.pages.router as pages

from app.database.connector import engine, get_db
from app.database import models
from app.image_tool import ImageManager

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Static Mount
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Routers for other modules
app.include_router(users.router)
app.include_router(buckets.router)
app.include_router(pages.router)

ig = ImageManager()

@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    """Main Home Page"""
    return templates.TemplateResponse("index.html",{"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_view(request: Request):
    """Login Page"""
    return templates.TemplateResponse("login.html",{"request": request})


@app.post("/upload_img")
async def upload_image(file: UploadFile):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    try:
        with open(f"/tmp/{file.filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        data = ig.upload_image(f"/tmp/{file.filename}")
        return {"succ":True, "message": "File uploaded successfully!", "filename":data}
    except Exception as e:
        return {"succ":False, "message": str(e)}


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


public_app = FastAPI()
public_app.mount("/static", StaticFiles(directory="static"), name="static")

# Public application
# We use hydration to keep backend secure (the frontend should not make ANY api requests) 

import app.users.crud as usermanage
import app.buckets.crud as bucketmanage
@public_app.get("/", response_class=HTMLResponse)
async def global_home_view(request: Request, db: Session = Depends(get_db)):
    """Home Page (lists users & top pages)"""
    users = usermanage.retrieve_users(db)
    buckets = bucketmanage.git_all_pub_buckets(db)

    return templates.TemplateResponse("public_home.html",{"request": request, "users":users, "buckets":buckets})


@public_app.get("/u/{username}/", response_class=HTMLResponse)
async def pub_buckets_view(request: Request, username: str, db: Session = Depends(get_db)):
    """Modified Buckets Page (lists users)"""
    user = usermanage.get_user_data(username, db)
    print(user.pfp)

    if ig.check_file_exists(user.pfp):

        ex_url = ig.retreve_image(user.pfp)
    else:
        ex_url = ig.retreve_image("icon.jpg")
    buckets = bucketmanage.get_buckets(username, db, vis_filter=True)

    return templates.TemplateResponse("public_profile.html",{
        "request": request, 
        "username":username, 
        "bio":user.bio, 
        "pfp":ex_url, 
        "buckets":buckets
    })


@public_app.get("/b/{bucketid}", response_class=HTMLResponse)
async def pub_sbucket_view(request: Request, bucketid: int, db: Session = Depends(get_db)):
    """Modified Single Bucket Page to show contents"""
    bucket = bucketmanage.get_bucket(bucketid, db)
    if bucket.visibility == False:
        bucket.name = "Private Content; Access Denied."
    
    buckets = bucketmanage.get_bucket_buckets(bucketid, db, vis_filter=True)
    pages = bucketmanage.get_bucket_pages(bucketid, db, True)

    return templates.TemplateResponse("public_bucket.html",{
        "request": request, 
        "name":bucket.name, 
        "pages":pages, 
        "buckets":buckets,
        "backurl": ("/" if bucket.bucket_owner_id is None else f"b/{bucket.bucket_owner_id}")
        })

from app.pages import crud
from app.users import functions

@public_app.get("/p/{pageid}", response_class=HTMLResponse)
async def pub_page_view(request: Request, pageid: int, db: Session = Depends(get_db)):
    """Modified Page view to show contents"""

    data = {
        "request": request, 
        "pg_title": "This page is not public.",
        "pg_cnt": "Please contact author to make this page public.",
        "pageid": pageid, 
    }
    page = crud.get_page(-1, pageid, db)
    if page and page.public:
            data["tbURL"] =  f"/b/{page.owner_id}/"

            page_list: list = bucketmanage.get_bucket_pages(page.owner_id, db, vis_filter=True)

            index: int = 0
            while index < len(page_list):
                if page_list[index]["id"] == page.id:
                    break

                index+=1
            
            nav = {}
            if index + 1 < len(page_list):
                data["next"] =  f"/p/{page_list[index + 1]['id']}"

            if index - 1 >= 0:
                data["back"] = f"/p/{page_list[index - 1]['id']}"

            page = crud.get_page(-1, pageid, db)
            data["pg_cnt"] = page.description.replace("[@@#%]", "\"")
            data["pg_title"] = page.title

    return templates.TemplateResponse("public_page.html", data)
