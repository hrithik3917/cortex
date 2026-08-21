from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import get_user_by_email
from app.auth.hashing import verify_password
from app.auth.jwt_handler import create_access_token
from app.schemas.token import TokenResponse
from app.exceptions.app_exceptions import InvalidCredentialsExceptions


def login_user(db: Session, email: str, password: str) -> TokenResponse:
    user = get_user_by_email(db, email)

    if not user:
        raise InvalidCredentialsExceptions()
    
    if not verify_password(password, user.hashed_password):
        raise InvalidCredentialsExceptions()
    
    token = create_access_token({"sub":user.email, "user_id": user.id})
    return TokenResponse(access_token=token, token_type="bearer")

