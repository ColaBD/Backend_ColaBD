import uuid
from app.database.module_schema.repository_schema import RepositorySchema
from app.models.dto.compartilhado.response import Response


class ServiceSchema:
    """Service layer for schema business logic."""
    
    def __init__(self):
        self.repo_schema = RepositorySchema()
    
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
                "database_model": str(uuid.uuid4())  # Convert UUID to string
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