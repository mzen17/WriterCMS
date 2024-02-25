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
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(users.router)
app.include_router(buckets.router)
app.include_router(pages.router)

templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("index.html",{"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html",{"request": request})


@app.get("/buckets", response_class=HTMLResponse)
async def pages(request: Request):
    return templates.TemplateResponse("buckets.html",{"request": request})


@app.get("/bucket/{id}", response_class=HTMLResponse)
async def pages(request: Request, id: int):
    return templates.TemplateResponse("sbucket.html",{"request": request, "id":id})


@app.get("/bucket/{bid}/page/{pid}", response_class=HTMLResponse)
async def pages(request: Request, bid: int, pid:int):
    return templates.TemplateResponse("page.html",{"request": request, "id":bid, "pid":pid})

