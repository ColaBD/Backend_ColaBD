from pymongo import MongoClient
from app.core import SECRETS


class RepositoryAuth:
  def __init__(self):
    client = MongoClient(SECRETS.CONNECTION)
    database = client.Colabd
    self.collection = database["User"]

  # Criar novo usuário
  async def create(self, user_data: dict) -> str:
    result = self.collection.insert_one(user_data)
    return str(result.inserted_id)
  
  async def findOne(self, user_received):
    return self.collection.find_one({"email": user_received.email})
