from app.models.dto.compartilhado.response import Response
from app.database.common.supabase_client import get_supabase_client
from supabase import Client

# import logging
# logging.basicConfig(level=logging.DEBUG)

class RepositoryUser:
  def __init__(self):
    self.supabase: Client = None
  
  def _get_supabase_client(self) -> Client:
    if self.supabase is None:
      self.supabase = get_supabase_client()
    return self.supabase

  async def create(self, user_received: dict) -> str:
    try:
      supabase = self._get_supabase_client()
      data_supabase = supabase.table("user").insert(user_received).execute()
      
      if not data_supabase.data:
        raise Exception("Erro ao criar usuário")
              
      return Response(data="Usuário registrado com sucesso!", success=True)
    
    except Exception as e:
      return Response(data=str(e), success=False)

  async def selectOne(self, user_received) -> dict:
    try: 
      supabase = self._get_supabase_client()
      data_supabase = supabase.table('user').select('*').eq("email", user_received.email).limit(1).execute()
      
      if not data_supabase.data:
        raise Exception("Usuário não encontrado")
        
      return Response(data=data_supabase.data[0], success=True)
    
    except Exception as e:
      return Response(data=str(e), success=False)