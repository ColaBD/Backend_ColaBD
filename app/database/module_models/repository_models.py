from typing import Optional, List, Dict, Any
from bson import ObjectId
from pymongo.errors import PyMongoError
from app.database.common.mongo_client import get_collection
from app.models.dto.compartilhado.response import Response
import logging

logger = logging.getLogger(__name__)


class RepositoryModels:

    def __init__(self):
        self.collection = get_collection('models')

    async def create(self, model_data: Dict[str, Any]) -> Response:
        try:
            result = self.collection.insert_one(model_data)
            
            if not result.inserted_id:
                raise Exception("Erro ao criar modelo")
            
            # Return the created document with its ID
            created_model = self.collection.find_one({"_id": result.inserted_id})
            created_model["_id"] = str(created_model["_id"])  # Convert ObjectId to string
            
            return Response(data=created_model, success=True)
            
        except PyMongoError as e:
            logger.error(f"MongoDB error while creating model: {str(e)}")
            return Response(data=f"Erro de banco de dados: {str(e)}", success=False)
        except Exception as e:
            logger.error(f"Error while creating model: {str(e)}")
            return Response(data=str(e), success=False)

    async def find_by_id(self, model_id: str) -> Response:
        try:
            object_id = ObjectId(model_id)
            model = self.collection.find_one({"_id": object_id})
            
            if not model:
                raise Exception("Modelo não encontrado")
            
            model["_id"] = str(model["_id"])
            
            return Response(data=model, success=True)
            
        except Exception as e:
            logger.error(f"Error while finding model by ID: {str(e)}")
            return Response(data=str(e), success=False)

    async def find_all(self, limit: Optional[int] = None, skip: Optional[int] = None) -> Response:
        try:
            cursor = self.collection.find()
            
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            models = list(cursor)
            
            # Convert ObjectIds to strings
            for model in models:
                model["_id"] = str(model["_id"])
            
            return Response(data=models, success=True)
            
        except Exception as e:
            logger.error(f"Error while finding all models: {str(e)}")
            return Response(data=str(e), success=False)

    async def update_by_id(self, model_id: str, update_data: Dict[str, Any]) -> Response:
        try:
            object_id = ObjectId(model_id)
            
            result = self.collection.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise Exception("Modelo não encontrado")
            
            if result.modified_count == 0:
                raise Exception("Nenhuma alteração foi feita")
            
            # Return the updated document
            updated_model = self.collection.find_one({"_id": object_id})
            updated_model["_id"] = str(updated_model["_id"])
            
            return Response(data=updated_model, success=True)
            
        except Exception as e:
            logger.error(f"Error while updating model: {str(e)}")
            return Response(data=str(e), success=False)

    async def delete_by_id(self, model_id: str) -> Response:
        try:
            object_id = ObjectId(model_id)
            
            result = self.collection.delete_one({"_id": object_id})
            
            if result.deleted_count == 0:
                raise Exception("Modelo não encontrado")
            
            return Response(data="Modelo deletado com sucesso", success=True)
            
        except Exception as e:
            logger.error(f"Error while deleting model: {str(e)}")
            return Response(data=str(e), success=False)

    async def find_by_criteria(self, criteria: Dict[str, Any], limit: Optional[int] = None) -> Response:
        try:
            cursor = self.collection.find(criteria)
            
            if limit:
                cursor = cursor.limit(limit)
            
            models = list(cursor)
            
            # Convert ObjectIds to strings
            for model in models:
                model["_id"] = str(model["_id"])
            
            return Response(data=models, success=True)
            
        except Exception as e:
            logger.error(f"Error while finding models by criteria: {str(e)}")
            return Response(data=str(e), success=False)