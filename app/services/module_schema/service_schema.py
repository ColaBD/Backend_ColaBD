import uuid
import logging
from app.database.module_schema.repository_schema import RepositorySchema
from app.database.module_schema.repository_cells import RepositoryCells
from app.models.dto.compartilhado.response import Response

logger = logging.getLogger(__name__)


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
        """Get all schemas for a specific user - optimized for speed."""
        try:
            logger.info(f"Service: Getting schemas for user {user_id}")
            
            # Get user schemas (lightweight query)
            result = await self.repo_schema.get_by_user_id(user_id)
            if not result.success:
                return result
            
            # Extract schema IDs for batch processing
            schema_ids = [user_schema["schema_id"] for user_schema in result.data]
            logger.info(f"Service: Found {len(schema_ids)} schemas for user")
            
            if not schema_ids:
                return Response(data=[], success=True)
            
            # Get all schema details in one optimized call
            schemas_result = await self.repo_schema.get_schemas_by_ids(schema_ids)
            if not schemas_result.success:
                logger.error(f"Service: Error getting schema details: {schemas_result.data}")
                return Response(data=[], success=True)  # Return empty instead of error
            
            # Process schemas and add signed URLs in parallel for better performance
            import asyncio
            
            async def process_schema(schema_data):
                """Process individual schema and get signed URL if needed."""
                schema_id = schema_data["id"]
                
                # Get signed URL for image (optimized - only if likely to have image)
                signed_image_url = None
                try:
                    # Quick check - only get signed URL, don't log errors for missing images
                    image_url_result = await self.repo_schema.get_schema_image_signed_url(schema_id)
                    if image_url_result.success and image_url_result.data:
                        signed_image_url = image_url_result.data
                except:
                    pass  # Silently ignore errors for missing images
                
                # Add signed URL to schema data
                schema_data["signed_image_url"] = signed_image_url
                return schema_data
            
            # Process all schemas in parallel for better performance
            schema_details_list = await asyncio.gather(
                *[process_schema(schema_data) for schema_data in schemas_result.data],
                return_exceptions=True
            )
            
            # Filter out any exceptions and keep only successful results
            schema_details_list = [
                result for result in schema_details_list 
                if not isinstance(result, Exception)
            ]
            
            logger.info(f"Service: Returning {len(schema_details_list)} schema details")
            return Response(data=schema_details_list, success=True)
            
        except Exception as e:
            logger.error(f"Service: Error in get_schemas_by_user: {str(e)}")
            return Response(data=str(e), success=False)
    
    async def update_schema(self, update_schema_data, current_user_id: str, display_picture=None) -> Response:
        """Update a schema with cells data and save cells to MongoDB. Also handle image upload if provided."""
        try:
            logger.info(f"Service: Starting update_schema for schema_id: {update_schema_data.schema_id}")
            schema_id = update_schema_data.schema_id
            cells_data = {"cells": update_schema_data.cells}
            
            # Step 1: Verify if the schema exists and belongs to the user
            logger.info("Service: Step 1 - Verifying schema exists")
            schema_result = await self.repo_schema.get_schema_by_id(schema_id)
            if not schema_result.success:
                logger.error(f"Service: Schema not found: {schema_result.data}")
                return Response(data="Schema não encontrado", success=False)
            logger.info("Service: Schema found successfully")
            
            # Step 2: Verify if user has access to this schema
            logger.info("Service: Step 2 - Verifying user permissions")
            user_schemas_result = await self.repo_schema.get_by_user_id(current_user_id)
            if not user_schemas_result.success:
                logger.error(f"Service: Error checking user permissions: {user_schemas_result.data}")
                return Response(data="Erro ao verificar permissões do usuário", success=False)
            
            # Check if user has access to this schema
            user_schema_ids = [us["schema_id"] for us in user_schemas_result.data]
            if schema_id not in user_schema_ids:
                logger.error(f"Service: User {current_user_id} does not have access to schema {schema_id}")
                return Response(data="Acesso negado: você não tem permissão para atualizar este schema", success=False)
            logger.info("Service: User permissions verified")
            
            # Step 3: Handle image upload if provided
            image_uploaded = False
            if display_picture:
                logger.info("Service: Step 3 - Processing image upload")
                upload_result = await self.repo_schema.upload_schema_image(schema_id, display_picture)
                if not upload_result.success:
                    logger.error(f"Service: Image upload failed: {upload_result.data}")
                    return Response(data=f"Erro no upload da imagem: {upload_result.data}", success=False)
                logger.info("Service: Image uploaded successfully")
                image_uploaded = True
            else:
                logger.info("Service: No image provided, skipping upload")
            
            # Step 4: Save cells data to MongoDB
            logger.info("Service: Step 4 - Saving cells to MongoDB")
            cells_result = await self.repo_cells.create_cells(cells_data)
            if not cells_result.success:
                logger.error(f"Service: Error saving cells: {cells_result.data}")
                return Response(data=f"Erro ao salvar células: {cells_result.data}", success=False)
            logger.info(f"Service: Cells saved successfully with ID: {cells_result.data}")
            
            # Step 5: Update schema with the MongoDB document ID as database_model
            logger.info("Service: Step 5 - Updating schema database_model")
            database_model_id = cells_result.data  # This is the MongoDB document ID
            update_result = await self.repo_schema.update_schema_database_model(schema_id, database_model_id)
            
            if not update_result.success:
                logger.error(f"Service: Error updating schema: {update_result.data}")
                return Response(data=f"Erro ao atualizar schema: {update_result.data}", success=False)
            logger.info("Service: Schema updated successfully")
            
            response_data = {
                "schema_id": schema_id,
                "database_model": database_model_id,
                "cells_count": len(update_schema_data.cells),
                "message": "Schema atualizado com sucesso"
            }
            
            if image_uploaded:
                response_data["image_uploaded"] = True
                response_data["message"] += " com imagem"
            
            logger.info(f"Service: update_schema completed successfully: {response_data}")
            return Response(data=response_data, success=True)
            
        except Exception as e:
            logger.error(f"Service: Unexpected error in update_schema: {str(e)}")
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