"""Basic auth router - skeleton implementation.
Returns a JWT token for any username/password for demo purposes.
In production, replace with real user DB and hashed-password checks.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt

from app.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


@router.post('/login', response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # For skeleton: accept any username/password
    if not form_data.username:
        raise HTTPException(status_code=400, detail="Username required")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}
