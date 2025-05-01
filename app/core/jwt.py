from app.core import SECRETS
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

ALGORITHM = "HS256"
EXPIRATION_MINUTES = 30

def create_access_token(data: dict):
  to_encode = data.copy()
  expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRATION_MINUTES)
  to_encode.update({"exp": expire})
  return jwt.encode(to_encode, SECRETS.SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
  try:
    payload = jwt.decode(token, SECRETS.SECRET_KEY, algorithms=[ALGORITHM])
    return payload
  except JWTError:
    return None