from fastapi import APIRouter, HTTPException

from app.models.dto.compartilhado.response import Response
from app.models.dto.module_auth.infoAuth import InfoAuth
from app.models.dto.module_auth.login_auth import LoginAuth
from app.services.module_user.service_user import ServiceAuth
from app.models.dto.module_auth.register_auth import RegisterAuth
from app.models.entities.module_user.user import User
from app.core.jwt import create_access_token

import logging
logging.basicConfig(level=logging.DEBUG)

service_user = ServiceAuth()
router = APIRouter()

def http_exception(result, status=500):
    raise HTTPException(detail=result.data, status_code=status)


@router.post("/auth/register", response_model=str, tags=["Autenticação"])
async def register(user_received: RegisterAuth):
  try:
    user = User(name=user_received.name, email=user_received.email, password=user_received.password)
    
  except ValueError as e:
    erro_msg = e.errors()[0]['msg']
    http_exception(Response(data=erro_msg), 400)

  result = await service_user.register_service(user)
  
  if (not result.success):
    http_exception(result)
  
  return result.data

@router.post("/auth/login", response_model=InfoAuth, tags=["Autenticação"])
async def login(user_received: LoginAuth):
  result = await service_user.login_service(user_received) 
  
  if (not result.success):
    http_exception(result, 400)

  return create_access_token(result.data)

@router.post("/auth/logout", tags=["Autenticação"])
async def logout(user_received: LoginAuth):   
  return True
