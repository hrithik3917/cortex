from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import (
    get_user_by_id,
    get_user_by_email,
    create_user as create_user_model,
    delete_user,
)
from app.schemas.user import UserCreate
from app.auth.hashing import hash_password

from app.exceptions.app_exceptions import (
    EmailAlreadyRegisteredException,
    UserNotFoundException
    )


def fetch_user(db: Session, user_id: int):
    user = get_user_by_id(user_id, db)
    if not user:
        raise UserNotFoundException(user_id)
    return user


def register_user(db: Session, user_data: UserCreate) -> object:
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise EmailAlreadyRegisteredException(user_data.email)
    
    hashed = hash_password(user_data.password)

    return create_user_model(db, user_data.email, hashed)


def remove_user(db: Session, user_id: int) -> None:
    fetch_user(db, user_id)
    delete_user(user_id, db)
