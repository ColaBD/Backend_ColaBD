from fastapi import APIRouter, HTTPException

from app.models.dto.compartilhado.response import Response
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

@router.post("/register")
async def register(user_received: RegisterAuth):
  try:
    user = User(name=user_received.name, email=user_received.email, password=user_received.password)
    
  except ValueError as e:
    erro_msg = e.errors()[0]['msg']
    http_exception(Response(data=erro_msg), 400)

  result = await service_user.register_service(user)
  
  if (not result.success):
    http_exception(result)
  
  return Response(data=result.data, status_code=200, success=result.success)

@router.post("/login")
async def login(user_received: LoginAuth):
  result = await service_user.login_service(user_received) 
  
  if (not result.success):
    http_exception(result, 400)

  userInfo = create_access_token(result.data)
  # token = create_access_token({"email": result.data["email"]})
  return Response(data=userInfo, status_code=200, success=True)

@router.post("/logout")
async def login(user_received: LoginAuth):   
  return True
