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

# router = APIRouter(dependencies=[Depends(decode_access_token (metodo do jwt.py))]) # -> Serve para proteger todas as rotas dentro do router
# no jwt já é possível pegar o id e nome (coisas que foram necessárias para gerar o jwt)

def http_exception(result, status=500):
  raise HTTPException(detail=result.data, status_code=status)

@router.post("/auth/register", response_model=Response, tags=["Autenticação"])
async def register(user_received: RegisterAuth):
  user = User(name=user_received.name, email=user_received.email, password=user_received.password)
  result = await service_user.register_service(user)
  
  if (not result.success):
    http_exception(result)
  
  return Response(data=result.data, status_code=200, success=True)

@router.post("/auth/login", response_model=Response, tags=["Autenticação"])
async def login(user_received: LoginAuth):
  result = await service_user.login_service(user_received) 
  if (not result.success):
    http_exception(result, 400)
    
  result_jwt = create_access_token(result.data)
  if (not result_jwt.success):
    http_exception(result, 400)

  return Response(data=result_jwt.data, status_code=200, success=True)
