from fastapi import FastAPI

from database import engine
from models import Base
from auth.routes import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="JWT Authentication")

app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "This JWT Auth API is running"}