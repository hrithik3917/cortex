from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserWithBooks
from app.schemas.book import MessageResponse
from app.services.user_service import fetch_user, register_user, remove_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user)


@router.get("/{user_id}", response_model=UserWithBooks)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return fetch_user(db, user_id)


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    remove_user(db, user_id)
    return {"message": f"User {user_id} and all their books deleted successfully"}
