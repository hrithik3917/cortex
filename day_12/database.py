from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL= "sqlite:///./user.db"

engine =create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def get_db():
    db: Session = SessionLocal()
    try: 
        yield db
    finally:
        db.close()