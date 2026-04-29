"""Auth Route."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(body: LoginRequest):
    from config.settings import settings
    from jose import jwt
    from datetime import datetime, timedelta
    if body.email != settings.ADMIN_EMAIL or body.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    payload = {"sub":body.email,"role":"admin","exp":datetime.utcnow()+timedelta(minutes=settings.JWT_EXPIRE_MINUTES)}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return {"access_token":token,"token_type":"bearer","role":"admin"}
