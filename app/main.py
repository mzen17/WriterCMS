"""Main method for application. Routes that return HTML."""

import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import app.users.router as users
import app.buckets.router as buckets
import app.pages.router as pages

from app.database.connector import engine
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

