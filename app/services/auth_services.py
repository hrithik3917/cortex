from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.user import get_user_by_email
from auth.hashing import verify_password
from auth.jwt_handler import create_access_token
from schemas.token import TokenResponse


def login_user(db: Session, email: str, password: str) -> TokenResponse:
    user = get_user_by_email(db, email)

    if not user:
        raise HTTPException(status_code=401, detail="User Not Found")
    
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token({"sub":user.email, "user_id": user.id})
    return TokenResponse(access_token=token, token_type="bearer")

