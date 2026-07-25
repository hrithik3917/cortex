from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from database import get_db
from models.user import get_user_by_id, User
from auth.jwt_handler import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db) ):
    payload = decode_access_token(token)

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token payload is missing user_id")
    
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")
    
    return user