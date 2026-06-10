from fastapi import Header, HTTPException
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()

def verify_token(token: str = Header(None)):
    if not token:
        raise HTTPException(status_code=401, detail="token not available")
    try:
        payload = jwt.decode(token, os.getenv("jwtsecretkey"), algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="token invalid or expired")
