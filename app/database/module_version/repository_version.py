from app.models.dto.compartilhado.response import Response
from app.database.common.supabase_client import get_supabase_client
from supabase import Client
import logging

logger = logging.getLogger(__name__)


class RepositoryVersion:
    def __init__(self):
        self.supabase: Client = None
    
    def _get_supabase_client(self) -> Client:
        if self.supabase is None:
            self.supabase = get_supabase_client()
        return self.supabase

    async def get_next_tag_for_schema(self, schema_id: str) -> Response:
        """Get the next tag number for a schema by finding the max tag + 1."""
        try:
            supabase = self._get_supabase_client()
            
            # Get all versions for this schema and find the max tag
            data_supabase = (
                supabase.table("schema_version")
                .select("version:version_id(tag)")
                .eq("schema_id", schema_id)
                .execute()
            )
            
            if not data_supabase.data:
                return Response(data=1, success=True)
            
            # Extract tags and find max
            tags = [item["version"]["tag"] for item in data_supabase.data if item.get("version") and item["version"].get("tag")]
            
            if not tags:
                return Response(data=1, success=True)
            
            next_tag = max(tags) + 1
            return Response(data=next_tag, success=True)
        
        except Exception as e:
            logger.error(f"Repo: Error getting next tag: {str(e)}")
            return Response(data=str(e), success=False)

    async def create_version(self, version_data: dict) -> Response:
        """Create a new version record."""
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("version").insert(version_data).execute()
            
            if not data_supabase.data:
                raise Exception("Erro ao criar versão")
            
            return Response(data=data_supabase.data[0], success=True)
        
        except Exception as e:
            logger.error(f"Repo: Error creating version: {str(e)}")
            return Response(data=str(e), success=False)

    async def create_schema_version(self, schema_version_data: dict) -> Response:
        """Create a schema-version relationship."""
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("schema_version").insert(schema_version_data).execute()
            
            if not data_supabase.data:
                raise Exception("Erro ao criar associação schema-versão")
            
            return Response(data=data_supabase.data[0], success=True)
        
        except Exception as e:
            logger.error(f"Repo: Error creating schema_version: {str(e)}")
            return Response(data=str(e), success=False)

    async def get_versions_by_schema_id(self, schema_id: str) -> Response:
        """Get all versions for a specific schema, similar to get_schemas_by_user_id."""
        try:
            supabase = self._get_supabase_client()

            data_supabase = (
                supabase.table("schema_version")
                .select("version_id, version!fk_schema_version_version(*)")
                .eq("schema_id", schema_id)
                .order("version(created_at)", desc=True)
                .execute()
            )

            schema_versions = data_supabase.data or []

            return Response(data=schema_versions, success=True)

        except Exception as e:
            logger.error(f"Repo: Error getting versions by schema id: {str(e)}")
            return Response(data=str(e), success=False)

    async def get_version_by_id(self, version_id: str) -> Response:
        """Get a specific version by its ID."""
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("version").select("*").eq("id", version_id).execute()
            
            if not data_supabase.data:
                raise Exception("Versão não encontrada")
            
            return Response(data=data_supabase.data[0], success=True)
        
        except Exception as e:
            logger.error(f"Repo: Error getting version by id: {str(e)}")
            return Response(data=str(e), success=False)


