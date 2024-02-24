from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.users import router
from app.database.connector import engine
from app.database import models


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router.router)


templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("index.html",{"request": request})


@app.get("/login", response_class=HTMLResponse)
async def lg_page(request: Request):
    return templates.TemplateResponse("login.html",{"request": request})
