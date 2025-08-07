from typing import List
from app.models.dto.compartilhado.response import Response
from app.database.common.supabase_client import get_supabase_client
from supabase import Client

# import logging
# logging.basicConfig(level=logging.DEBUG)


class RepositorySchema:
    """Repository for managing schema and user_schema table operations."""
    
    def __init__(self):
        self.supabase: Client = None
    
    def _get_supabase_client(self) -> Client:
        """Get Supabase client, initializing if needed."""
        if self.supabase is None:
            self.supabase = get_supabase_client()
        return self.supabase

    async def get_all(self) -> Response:
        """Get all user schema associations."""
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("user_schema").select("*").execute()
            
            return Response(data=data_supabase.data, success=True)
        
        except Exception as e:
            return Response(data=str(e), success=False)

    async def create(self, schema_data: dict) -> Response:
        """Create a new user schema association."""
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("user_schema").insert(schema_data).execute()
            
            if not data_supabase.data:
                raise Exception("Erro ao criar associação schema-usuário")
            
            return Response(data=data_supabase.data[0], success=True)
        
        except Exception as e:
            return Response(data=str(e), success=False)

    async def get_by_user_id(self, user_id: str) -> Response:
        """Get all schemas for a specific user."""
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("user_schema").select("*").eq("user_id", user_id).execute()
            
            return Response(data=data_supabase.data, success=True)
        
        except Exception as e:
            return Response(data=str(e), success=False)

    async def get_by_schema_id(self, schema_id: str) -> Response:
        """Get all users for a specific schema."""
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("user_schema").select("*").eq("schema_id", schema_id).execute()
            
            return Response(data=data_supabase.data, success=True)
        
        except Exception as e:
            return Response(data=str(e), success=False)

    async def create_schema(self, schema_data: dict) -> Response:
        """Create a new schema in the schema table."""
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("schema").insert(schema_data).execute()
            
            if not data_supabase.data:
                raise Exception("Erro ao criar schema")
            
            return Response(data=data_supabase.data[0], success=True)
        
        except Exception as e:
            return Response(data=str(e), success=False)

    async def create_user_schema(self, user_schema_data: dict) -> Response:
        """Create a new user schema association."""
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("user_schema").insert(user_schema_data).execute()
            
            if not data_supabase.data:
                raise Exception("Erro ao criar associação schema-usuário")
            
            return Response(data=data_supabase.data[0], success=True)
        
        except Exception as e:
            return Response(data=str(e), success=False)