from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
from app.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

class AuthData(BaseModel):
    username: str

@router.post('/login')
async def login(data: AuthData):
    # NOTE: This is a minimal stub for demo purposes. Replace with real user lookup & password checks.
    if not data.username:
        raise HTTPException(status_code=400, detail='username required')
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({'sub': data.username, 'exp': expire}, SECRET_KEY, algorithm='HS256')
    return {'access_token': token, 'token_type': 'bearer'}
