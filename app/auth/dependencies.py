from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from app.database import get_db
from app.models.user import get_user_by_id, User
from app.auth.jwt_handler import decode_access_token

from app.exceptions.app_exceptions import (
    InvalidTokenException,
    UserNotFoundException
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db) ):
    payload = decode_access_token(token)

    user_id = payload.get("user_id")
    if not user_id:
        raise InvalidTokenException()
    
    user = get_user_by_id(user_id, db)
    if not user:
        raise UserNotFoundException()
    
    return user