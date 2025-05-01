from fastapi import APIRouter

from app.models.entities.module_auth.login_auth import LoginAuth
from app.services.module_auth.service_auth import ServiceAuth
from app.models.entities.module_auth.register_auth import RegisterAuth
from app.models.entities.module_auth.token import Token
from app.core.jwt import create_access_token

service_auth = ServiceAuth()
router = APIRouter()

class ControllerUser:
  
  @router.post("/register")
  async def register(user_auth: RegisterAuth):
    user_id = await service_auth.register_service(user_auth)
    
    return { "id": user_id }

  @router.post("/login")
  async def login(user_received: LoginAuth):
    user = await service_auth.login_service(user_received)
    token = create_access_token({"email": user["email"]})
    return Token(access_token=token, token_type='bearer')
