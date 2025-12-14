import uuid
import logging
from app.database.module_version.repository_version import RepositoryVersion
from app.database.module_schema.repository_schema import RepositorySchema
from app.models.dto.compartilhado.response import Response

logger = logging.getLogger(__name__)


class ServiceVersion:
    
    def __init__(self):
        self.repo_version = RepositoryVersion()
        self.repo_schema = RepositorySchema()
    
    async def create_version(self, create_version_data, current_user_id: str) -> Response:
        """Create a new version for a schema."""
        try:
            schema_id = create_version_data.schema_id
            
            logger.info(f"Service: Creating version for schema {schema_id}")
            
            # Step 1: Verify schema exists
            schema_result = await self.repo_schema.get_schema_by_id(schema_id)
            if not schema_result.success:
                logger.error(f"Service: Schema not found: {schema_result.data}")
                return Response(data="Schema não encontrado", success=False)
            
            # Step 2: Verify user has access to this schema
            user_schemas_result = await self.repo_schema.get_by_user_id(current_user_id)
            if not user_schemas_result.success:
                logger.error(f"Service: Error checking user permissions: {user_schemas_result.data}")
                return Response(data="Erro ao verificar permissões do usuário", success=False)
            
            user_schema_ids = [us["schema_id"] for us in user_schemas_result.data]
            if schema_id not in user_schema_ids:
                logger.error(f"Service: User {current_user_id} does not have access to schema {schema_id}")
                return Response(data="Acesso negado: você não tem permissão para versionar este schema", success=False)
            
            # Step 4: Create the version
            version_id = str(uuid.uuid4())
            version_dict = {
                "id": version_id,
                "tag": 1,
                "created_by": current_user_id,
                "comment": create_version_data.comment,
                "data": create_version_data.data
            }
            
            version_result = await self.repo_version.create_version(version_dict)
            if not version_result.success:
                logger.error(f"Service: Failed to create version: {version_result.data}")
                return Response(data=f"Erro ao criar versão: {version_result.data}", success=False)
            
            logger.info(f"Service: Version created with id {version_id}")
            
            # Step 5: Create schema-version relationship
            schema_version_dict = {
                "id": str(uuid.uuid4()),
                "schema_id": schema_id,
                "version_id": version_id
            }
            
            schema_version_result = await self.repo_version.create_schema_version(schema_version_dict)
            if not schema_version_result.success:
                logger.error(f"Service: Failed to create schema-version relationship: {schema_version_result.data}")
                return Response(data=f"Erro ao criar associação schema-versão: {schema_version_result.data}", success=False)
            
            logger.info(f"Service: Schema-version relationship created")
            
            return Response(
                data={
                    "version_id": version_id,
                    "schema_id": schema_id,
                    "tag": 1,
                    "message": "Versão criada com sucesso"
                },
                success=True
            )
            
        except Exception as e:
            logger.error(f"Service: Unexpected error in create_version: {str(e)}")
            return Response(data=str(e), success=False)
    
    async def get_versions_by_schema(self, schema_id: str, current_user_id: str) -> Response:
        """Get all versions for a specific schema."""
        try:
            logger.info(f"Service: Getting versions for schema {schema_id}")
            
            # Get versions from schema_version table
            result = await self.repo_version.get_versions_by_schema_id(schema_id)
            
            if not result.success:
                return result
            
            version_details_list = result.data or []
            logger.info(f"Service: Returning {len(version_details_list)} version details")
            
            return Response(data=version_details_list, success=True)
            
        except Exception as e:
            logger.error(f"Service: Error in get_versions_by_schema: {str(e)}")
            return Response(data=str(e), success=False)


