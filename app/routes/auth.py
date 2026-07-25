from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from schemas.token import TokenResponse
from services.auth_services import login_user
from typing import Annotated

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/login", response_model=TokenResponse)
def login(credentials: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):

    user = login_user(db, credentials.username, credentials.password)
    return user