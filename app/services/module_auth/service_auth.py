from fastapi import HTTPException

from app.database.module_auth.repository_auth import RepositoryAuth
from app.core.security import hash_password, verify_password

repo_user = RepositoryAuth()

class ServiceAuth:
  async def register_service(self, user_auth):
    user_dict = user_auth.dict()
    user_dict["password"] = hash_password(user_auth.password)
    
    return await repo_user.create(user_dict)
  
  async def login_service(self, user_received):
    user = await repo_user.findOne(user_received)
    if not user:
      raise HTTPException(status_code=400, detail="Usuário não encontrado")

    if not verify_password(user_received.password, user["password"]):
      raise HTTPException(status_code=400, detail="Senha inválida")
    
    return user