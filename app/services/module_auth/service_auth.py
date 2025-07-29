from app.database.module_auth.repository_auth import RepositoryAuth
from app.core.security import gerar_hash_senha, verificar_hash_senha
from app.models.dto.compartilhado.response import Response

#["atributo"] → quando você está acessando um dicionário (dict)
#.atributo → quando você está acessando um atributo de uma classe (objeto Python comum)

class ServiceAuth:
  
  def __init__(self):
    self.repo_user = RepositoryAuth()
      
  async def register_service(self, user_received):
    user_dict = user_received.dict()
    user_dict["password"] = gerar_hash_senha(user_received.password)
    
    result_create = await self.repo_user.create(user_dict)
    
    return result_create
    
  async def login_service(self, user_received):
    try: 
      result_selectOne = await self.repo_user.selectOne(user_received)
  
      if (result_selectOne.success):
        equal_password = verificar_hash_senha(user_received.password, result_selectOne.data["password"])
        
        if (not equal_password):
          raise Exception("Senha incorreta")
      
      return result_selectOne 
    
    except Exception as e:
      return Response(data=str(e), success=False)