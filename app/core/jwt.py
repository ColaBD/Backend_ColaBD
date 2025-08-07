from datetime import datetime, timedelta, timezone
from app.models.dto.compartilhado.response import Response
from app.models.dto.module_auth.infoAuth import InfoAuth
from jose import jwt, JWTError
import os

ALGORITHM = "HS256"
EXPIRATION_MINUTES = 30

def create_access_token(data: dict):
  expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRATION_MINUTES)
  
  to_encode = { # necessário, porque vai usar apenas o email e id para a criação do jwt e deve passar um dict
    "id": data["id"],
    "email": data["email"]
  }

  jwt_token = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=ALGORITHM)
  
  return Response(data=InfoAuth(access_token=jwt_token, exp=expire, token_type="Bearer"), success=True)

def decode_access_token(token: str): # -> necessário para futuros metodos que precisam saber quem é o usuario
  try:
    payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[ALGORITHM])
    user_id = payload.get("id")
    user_email = payload.get("email")
    
    if (user_email is None or user_id is None):
      raise Exception("Token inválido")
    
    return Response(data=payload, success=True)

  except Exception as e:
    return Response(data=str(e), success=False)
