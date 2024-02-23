from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.routers import user


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user.router)


templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("index.html",{"request": request})


@app.get("/login", response_class=HTMLResponse)
async def lg_page(request: Request):
    return templates.TemplateResponse("login.html",{"request": request})
