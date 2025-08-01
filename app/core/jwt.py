from datetime import datetime, timedelta, timezone
from app.models.dto.module_auth.infoAuth import InfoAuth
from app.models.dto.module_user.user import User
from jose import jwt, JWTError
import os

ALGORITHM = "HS256"
EXPIRATION_MINUTES = 30

def create_access_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRATION_MINUTES)
    
    to_encode = { # necessário, porque vai usar apenas o email para a criação do jwt e deve passar um dict
      "email": data["email"]
    }

    jwt_token = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=ALGORITHM)

    user_dto = User(id=data["id"], name=data["name"], email=data["email"])

    return InfoAuth(access_token=jwt_token, exp=expire, token_type="Bearer", user_info=user_dto)

def verify_access_token(token: str):
  try:
    payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[ALGORITHM])
    return payload
  
  except JWTError:
    return None
