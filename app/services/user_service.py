from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.user import (
    get_user_by_id,
    get_user_by_email,
    create_user as create_user_model,
    delete_user,
)
from schemas.user import UserCreate
from auth.hashing import hash_password


def fetch_user(db: Session, user_id: int):
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user


def register_user(db: Session, user_data: UserCreate) -> object:
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail=f"Email '{user_data.email}' is already registered"
        )
    
    hashed = hash_password(user_data.password)

    return create_user_model(db, user_data.email, hashed)


def remove_user(db: Session, user_id: int) -> None:
    fetch_user(db, user_id)
    delete_user(user_id, db)
