from typing import Dict, Any
from bson import ObjectId
from pymongo.errors import PyMongoError
from pymongo.collection import Collection
from app.database.common.mongo_client import get_collection
from app.models.dto.compartilhado.response import Response
from app.models.entities.module_schema.cells_model import CellsModel
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RepositoryCells:
    """
    Repository class for managing cells data in MongoDB models collection.
    """

    def __init__(self):
        self.collection: Collection = None

    def _get_collection(self) -> Collection:
        """Get MongoDB collection, initializing if needed."""
        if self.collection is None:
            self.collection = get_collection('models')  # Changed from 'cells' to 'models'
        return self.collection

    async def create_cells(self, cells_data: Dict[str, Any]) -> Response:
        """
        Create a new cells document in the MongoDB models collection.
        
        Args:
            cells_data: Dictionary containing cells data
            
        Returns:
            Response object with success status and the MongoDB document ID
        """
        try:
            # Create cells model with timestamps
            cells_model = CellsModel(**cells_data)
            cells_dict = cells_model.dict()
            
            collection = self._get_collection()
            result = collection.insert_one(cells_dict)
            
            if not result.inserted_id:
                raise Exception("Erro ao salvar células no MongoDB")
            
            # Return the MongoDB document ID as string
            return Response(data=str(result.inserted_id), success=True)
            
        except PyMongoError as e:
            logger.error(f"MongoDB error while creating cells: {str(e)}")
            return Response(data=f"Erro de banco de dados: {str(e)}", success=False)
        except Exception as e:
            logger.error(f"Error while creating cells: {str(e)}")
            return Response(data=str(e), success=False)

    async def get_cells_by_id(self, cells_id: str) -> Response:
        """
        Get cells document by its MongoDB ID from models collection.
        
        Args:
            cells_id: String representation of the MongoDB document ID
            
        Returns:
            Response object with cells data
        """
        try:
            object_id = ObjectId(cells_id)
            
            collection = self._get_collection()
            cells_doc = collection.find_one({"_id": object_id})
            
            if not cells_doc:
                raise Exception("Células não encontradas")
            
            # Convert ObjectId to string
            cells_doc["_id"] = str(cells_doc["_id"])
            
            return Response(data=cells_doc, success=True)
            
        except Exception as e:
            logger.error(f"Error while getting cells by ID: {str(e)}")
            return Response(data=str(e), success=False)

    async def update_cells_by_id(self, cells_id: str, cells_data: Dict[str, Any]) -> Response:
        """
        Update cells document by its MongoDB ID in models collection.
        
        Args:
            cells_id: String representation of the MongoDB document ID
            cells_data: Dictionary containing updated cells data
            
        Returns:
            Response object with success status
        """
        try:
            object_id = ObjectId(cells_id)
            
            # Add updated timestamp
            update_data = {
                **cells_data,
                "updated_at": datetime.now()
            }
            
            collection = self._get_collection()
            result = collection.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise Exception("Células não encontradas")
            
            return Response(data="Células atualizadas com sucesso", success=True)
            
        except Exception as e:
            logger.error(f"Error while updating cells: {str(e)}")
            return Response(data=str(e), success=False) 