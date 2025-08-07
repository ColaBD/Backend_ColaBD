import uuid
from app.database.module_schema.repository_schema import RepositorySchema
from app.database.module_schema.repository_cells import RepositoryCells
from app.models.dto.compartilhado.response import Response


class ServiceSchema:
    """Service layer for schema business logic."""
    
    def __init__(self):
        self.repo_schema = RepositorySchema()
        self.repo_cells = RepositoryCells()
    
    async def get_all_schemas(self) -> Response:
        """Get all user schema associations."""
        try:
            result = await self.repo_schema.get_all()
            return result
        except Exception as e:
            return Response(data=str(e), success=False)
    
    async def create_schema(self, create_schema_data, user_id: str) -> Response:
        """Create a new schema and associate it with the user."""
        try:
            # Step 1: Create the schema in the schema table
            schema_id = str(uuid.uuid4())
            
            # Create schema data for database insertion (let DB handle timestamps)
            schema_dict = {
                "id": schema_id,
                "title": create_schema_data.title,
                "display_picture": "",  # Empty string as default
                # database_model will be set later during update_schema
            }
            
            # Save schema to database
            schema_result = await self.repo_schema.create_schema(schema_dict)
            
            if not schema_result.success:
                raise Exception(f"Failed to create schema: {schema_result.data}")
            
            # Step 2: Create the user-schema association data (let DB handle timestamps)
            user_schema_dict = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "schema_id": schema_id
            }
            
            # Save user-schema association
            user_schema_result = await self.repo_schema.create_user_schema(user_schema_dict)
            
            if not user_schema_result.success:
                raise Exception(f"Failed to create user-schema association: {user_schema_result.data}")
            
            return Response(
                data={
                    "schema_id": schema_id,
                    "title": create_schema_data.title,
                    "message": "Schema created and associated with user successfully"
                }, 
                success=True
            )
            
        except Exception as e:
            return Response(data=str(e), success=False)
    
    async def get_schemas_by_user(self, user_id: str) -> Response:
        """Get all schemas for a specific user."""
        try:
            result = await self.repo_schema.get_by_user_id(user_id)
            return result
        except Exception as e:
            return Response(data=str(e), success=False)
    
    async def update_schema(self, update_schema_data, current_user_id: str) -> Response:
        """Update a schema with cells data and save cells to MongoDB."""
        try:
            schema_id = update_schema_data.schema_id
            cells_data = {"cells": update_schema_data.cells}
            
            # Step 1: Verify if the schema exists and belongs to the user
            schema_result = await self.repo_schema.get_schema_by_id(schema_id)
            if not schema_result.success:
                return Response(data="Schema não encontrado", success=False)
            
            # Step 2: Verify if user has access to this schema
            user_schemas_result = await self.repo_schema.get_by_user_id(current_user_id)
            if not user_schemas_result.success:
                return Response(data="Erro ao verificar permissões do usuário", success=False)
            
            # Check if user has access to this schema
            user_schema_ids = [us["schema_id"] for us in user_schemas_result.data]
            if schema_id not in user_schema_ids:
                return Response(data="Acesso negado: você não tem permissão para atualizar este schema", success=False)
            
            # Step 3: Save cells data to MongoDB
            cells_result = await self.repo_cells.create_cells(cells_data)
            if not cells_result.success:
                return Response(data=f"Erro ao salvar células: {cells_result.data}", success=False)
            
            # Step 4: Update schema with the MongoDB document ID as database_model
            database_model_id = cells_result.data  # This is the MongoDB document ID
            update_result = await self.repo_schema.update_schema_database_model(schema_id, database_model_id)
            
            if not update_result.success:
                return Response(data=f"Erro ao atualizar schema: {update_result.data}", success=False)
            
            return Response(
                data={
                    "schema_id": schema_id,
                    "database_model": database_model_id,
                    "cells_count": len(update_schema_data.cells),
                    "message": "Schema atualizado com sucesso"
                }, 
                success=True
            )
            
        except Exception as e:
            return Response(data=str(e), success=False)

    async def get_schema_with_cells(self, schema_id: str, current_user_id: str) -> Response:
        """Get schema by ID with cells data from MongoDB."""
        try:
            # Step 1: Verify if the schema exists
            schema_result = await self.repo_schema.get_schema_by_id(schema_id)
            if not schema_result.success:
                return Response(data="Schema não encontrado", success=False)
            
            schema_data = schema_result.data
            
            # Step 2: Verify if user has access to this schema
            user_schemas_result = await self.repo_schema.get_by_user_id(current_user_id)
            if not user_schemas_result.success:
                return Response(data="Erro ao verificar permissões do usuário", success=False)
            
            # Check if user has access to this schema
            user_schema_ids = [us["schema_id"] for us in user_schemas_result.data]
            if schema_id not in user_schema_ids:
                return Response(data="Acesso negado: você não tem permissão para acessar este schema", success=False)
            
            # Step 3: Get cells data from MongoDB if database_model exists
            cells_data = None
            if schema_data.get("database_model"):
                cells_result = await self.repo_cells.get_cells_by_id(schema_data["database_model"])
                if cells_result.success:
                    cells_data = cells_result.data
            
            # Step 4: Combine schema and cells data
            response_data = {
                "schema": schema_data,
                "cells": cells_data.get("cells", []) if cells_data else [],
                "has_cells": cells_data is not None,
                "database_model_id": schema_data.get("database_model")
            }
            
            return Response(data=response_data, success=True)
            
        except Exception as e:
            return Response(data=str(e), success=False)