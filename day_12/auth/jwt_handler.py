from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import FastAPI, HTTPException, status
from datetime import datetime, timedelta, timezone


SECRET_KEY="25de178fdb260be8ab91269de54bd2bfa1224b7d4b91f9b85e575ac0f1aa15cc"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes = TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_token



def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        return payload
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has Expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    