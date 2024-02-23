from fastapi import APIRouter
from app import fmodels

router = APIRouter()

@router.post("/users/create")
async def create_user(user: fmodels.Credentials):
    return {"resp":"?"}


@router.post("authenticate")
async def login(creds: fmodels.Credentials):
    pass