from fastapi import APIRouter, HTTPException

from app.models.dto.compartilhado.response import Response_Controller
from app.models.entities.module_auth.login_auth import LoginAuth
from app.services.module_auth.service_auth import ServiceAuth
from app.models.entities.module_auth.register_auth import RegisterAuth
from app.models.entities.module_auth.token import Token
from app.core.jwt import create_access_token

service_auth = ServiceAuth()
router = APIRouter()

def http_exception(result, status=500):
  raise HTTPException(detail=result.data, status_code=status)

@router.post("/register")
async def register(user_received: RegisterAuth):
  result = await service_auth.register_service(user_received)
  
  if (not result.success):
    http_exception(result)
  
  return Response_Controller(result.data, 200, result.success)

@router.post("/login")
async def login(user_received: LoginAuth):
  result = await service_auth.login_service(user_received) 
  
  if (not result.success):
    http_exception(result, 400)
    
  token = create_access_token({"email": result.data["email"]})
  
  return Response_Controller(Token(access_token=token, token_type='Bearer'), 200, True)

@router.post("/logout")
async def login(user_received: LoginAuth):   
  return True
