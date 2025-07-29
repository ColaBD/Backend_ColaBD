from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import os

ALGORITHM = "HS256"
EXPIRATION_MINUTES = 30

def create_access_token(data: dict):
  to_encode = data.copy()
  expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRATION_MINUTES)
  to_encode.update({"exp": expire})
  
  return jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm=ALGORITHM)

def verify_access_token(token: str):
  try:
    payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[ALGORITHM])
    return payload
  
  except JWTError:
    return None