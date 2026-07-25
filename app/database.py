import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    load_dotenv = None

DATABASE_URL = os.getenv("DATABASE_URL")

# if not DATABASE_URL:
#     raise RuntimeError("DATABASE_URL is not set. Please define it in the environment or .env file.")

# if DATABASE_URL.startswith("sqlite"):
#     engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})
# else:
#     engine = create_engine(DATABASE_URL, echo=True)
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()