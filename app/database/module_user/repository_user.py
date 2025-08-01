from app.models.dto.compartilhado.response import Response
from supabase import create_client, Client
import os

# import logging
# logging.basicConfig(level=logging.DEBUG)

class RepositoryUser:
  def __init__(self):
    self.supabase: Client = create_client(os.getenv('CONNECTION_POSTGRES_SUPABASE'), os.getenv('SECRET_KEY_POSTGRES_SUPABASE'))

  async def create(self, user_received: dict) -> str:
    try:
      data_supabase = self.supabase.table("user").insert(user_received).execute()
      
      if not data_supabase.data:
        raise Exception("Erro ao criar usuário")
              
      return Response(data="Usuário registrado com sucesso!", success=True)
    
    except Exception as e:
      return Response(data=str(e), success=False)

  async def selectOne(self, user_received) -> dict:
    try: 
      data_supabase = self.supabase.table('user').select('*').eq("email", user_received.email).limit(1).execute()
      
      if not data_supabase.data:
        raise Exception("Usuário não encontrado")
        
      return Response(data=data_supabase.data[0], success=True)
    
    except Exception as e:
      return Response(data=str(e), success=False)