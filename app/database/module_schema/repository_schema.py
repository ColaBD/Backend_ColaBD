from app.models.dto.compartilhado.response import Response
from app.database.common.supabase_client import get_supabase_client
from supabase import Client
from fastapi import UploadFile
from supabase import create_client
from app.database.common.supabase_public_url import build_public_url
import logging
import os

logger = logging.getLogger(__name__)

class RepositorySchema:
    def __init__(self):
        self.supabase: Client = None
    
    def _get_supabase_client(self) -> Client:
        if self.supabase is None:
            self.supabase = get_supabase_client()
        return self.supabase

    async def get_all(self) -> Response:
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("user_schema").select("*").execute()
            
            return Response(data=data_supabase.data, success=True)
        
        except Exception as e:
            return Response(data=str(e), success=False)

    async def create(self, schema_data: dict) -> Response:
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("user_schema").insert(schema_data).execute()
            
            if not data_supabase.data:
                raise Exception("Erro ao criar associação schema-usuário")
            
            return Response(data=data_supabase.data[0], success=True)
        
        except Exception as e:
            return Response(data=str(e), success=False)

    async def get_by_user_id(self, user_id: str) -> Response:
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("user_schema").select("*").eq("user_id", user_id).execute()
            
            return Response(data=data_supabase.data, success=True)
        
        except Exception as e:
            return Response(data=str(e), success=False)

    async def get_by_schema_id(self, schema_id: str) -> Response:
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("user_schema").select("*").eq("schema_id", schema_id).execute()
            
            return Response(data=data_supabase.data, success=True)
        
        except Exception as e:
            return Response(data=str(e), success=False)

    async def create_schema(self, schema_data: dict) -> Response:
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("schema").insert(schema_data).execute()
            
            if not data_supabase.data:
                raise Exception("Erro ao criar schema")
            
            return Response(data=data_supabase.data[0], success=True)
        
        except Exception as e:
            return Response(data=str(e), success=False)

    async def create_user_schema(self, user_schema_data: dict) -> Response:
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("user_schema").insert(user_schema_data).execute()
            
            if not data_supabase.data:
                raise Exception("Erro ao criar associação schema-usuário")
            
            return Response(data=data_supabase.data[0], success=True)
        
        except Exception as e:
            return Response(data=str(e), success=False)

    async def update_schema_database_model(self, schema_id: str, database_model_id: str) -> Response:
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("schema").update({
                "database_model": database_model_id,
                "updated_at": "now()"
            }).eq("id", schema_id).execute()
            
            if not data_supabase.data:
                raise Exception("Erro ao atualizar schema com database_model")
            
            return Response(data=data_supabase.data[0], success=True)
        
        except Exception as e:
            error_message = str(e)
            if "invalid input syntax for type uuid" in error_message:
                return Response(
                    data="Erro: O campo database_model no banco de dados está configurado como UUID, mas está recebendo um ObjectId do MongoDB. "
                         "O campo precisa ser alterado para TEXT/VARCHAR no banco de dados, ou o valor precisa ser convertido para UUID.",
                    success=False
                )
            return Response(data=str(e), success=False)

    async def get_schema_by_id(self, schema_id: str) -> Response:
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("schema").select("*").eq("id", schema_id).execute()
            
            if not data_supabase.data:
                raise Exception("Schema não encontrado")
            
            return Response(data=data_supabase.data[0], success=True)
        
        except Exception as e:
            return Response(data=str(e), success=False)

    async def get_schemas_by_ids(self, schema_ids: list) -> Response:
        try:
            if not schema_ids:
                return Response(data=[], success=True)
            
            supabase = self._get_supabase_client()
            
            # Use 'in' filter for batch query
            data_supabase = supabase.table("schema").select("*").in_("id", schema_ids).execute()
            
            return Response(data=data_supabase.data or [], success=True)
        
        except Exception as e:
            return Response(data=str(e), success=False)

    async def upload_schema_image(self, schema_id: str, image_file: UploadFile) -> Response:
        try:           
            logger.info(f"Repository: Starting image upload for schema {schema_id}")
            logger.info(f"Repository: Image file - name: {image_file.filename}, type: {image_file.content_type}, size: {image_file.size}")
            
            # Use bucket-specific key for storage operations (strip to avoid hidden newlines)
            connection_url = (os.getenv('CONNECTION_POSTGRES_SUPABASE') or '').strip()
            bucket_key = (os.getenv('SECRET_SUPABASE_BUCKET') or '').strip()
            
            if not bucket_key:
                logger.error("SECRET_SUPABASE_BUCKET environment variable not found")
                return Response(data="Configuração de bucket não encontrada", success=False)
            
            logger.info("Repository: Using bucket-specific key for upload")
            supabase = create_client(connection_url, bucket_key)
            
            # Validate file size (limit to 10MB)
            if image_file.size and image_file.size > 10 * 1024 * 1024:
                return Response(data="Arquivo muito grande. Máximo permitido: 10MB", success=False)
            
            # Read file content
            logger.info("Repository: Reading file content...")
            file_content = await image_file.read()
            logger.info(f"Repository: File content read successfully, size: {len(file_content)} bytes")
            
            # Reset file pointer for potential future reads
            await image_file.seek(0)
            
            # Determine file extension based on content type
            extension = "png"
            if image_file.content_type:
                if "jpeg" in image_file.content_type or "jpg" in image_file.content_type:
                    extension = "jpg"
                elif "gif" in image_file.content_type:
                    extension = "gif"
                elif "webp" in image_file.content_type:
                    extension = "webp"
            
            # Upload to schemas-storage bucket with schema_id as filename
            file_path = f"{schema_id}.{extension}"
            logger.info(f"Repository: Uploading to path: {file_path}")
            
            upload_response = supabase.storage.from_("schemas-storage").upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": image_file.content_type or "image/png",
                    "upsert": "true"  # String instead of boolean - Supabase expects string
                }
            )
            
            logger.info(f"Repository: Upload response received: {type(upload_response)}")
            
            # Check for errors in different response formats
            if hasattr(upload_response, 'error') and upload_response.error:
                logger.error(f"Repository: Upload error (hasattr): {upload_response.error}")
                raise Exception(f"Erro no upload da imagem: {upload_response.error}")
            
            # Some Supabase clients return dict with error key
            if isinstance(upload_response, dict) and upload_response.get('error'):
                logger.error(f"Repository: Upload error (dict): {upload_response['error']}")
                raise Exception(f"Erro no upload da imagem: {upload_response['error']}")
            
            logger.info("Repository: Image uploaded successfully")
            return Response(data={"file_path": file_path, "message": "Imagem enviada com sucesso"}, success=True)
        
        except Exception as e:
            logger.error(f"Repository: Upload failed with exception: {str(e)}")
            return Response(data=str(e), success=False)

    async def get_schema_image_signed_url(self, schema_id: str) -> Response:
        try:
            # Use bucket-specific key for storage operations (strip to avoid hidden newlines)
            connection_url = (os.getenv('CONNECTION_POSTGRES_SUPABASE') or '').strip()
            bucket_key = (os.getenv('SECRET_SUPABASE_BUCKET') or '').strip()
            
            if not bucket_key:
                logger.error("SECRET_SUPABASE_BUCKET environment variable not found")
                return Response(data="Configuração de bucket não encontrada", success=False)
            
            supabase = create_client(connection_url, bucket_key)
            
            # Try most common extensions first for speed
            extensions = ["png", "jpg"]  # Only try most common extensions for speed
            
            for extension in extensions:
                file_path = f"{schema_id}.{extension}"
                
                try:
                    # Generate signed URL valid for 1 hour (3600 seconds)
                    signed_url_response = supabase.storage.from_("schemas-storage").create_signed_url(
                        path=file_path,
                        expires_in=3600
                    )
                    
                    # Check if request was successful
                    if hasattr(signed_url_response, 'error') and signed_url_response.error:
                        if "not found" in str(signed_url_response.error).lower():
                            continue  
                        continue  
                    
                    # Some clients return dict with error
                    if isinstance(signed_url_response, dict) and signed_url_response.get('error'):
                        if "not found" in str(signed_url_response['error']).lower():
                            continue  
                        continue  
                    
                    signed_url = signed_url_response.get('signedURL') or signed_url_response.get('signed_url')
                    if signed_url:
                        return Response(data=signed_url, success=True)
                        
                except Exception as e:
                    continue  
            
            # As fallback, return a public URL if object exists and bucket policy allows public
            try:
                for extension in extensions:
                    file_path = f"{schema_id}.{extension}"
                    public_url = build_public_url("schemas-storage", file_path)
                    return Response(data=public_url, success=True)
            except Exception:
                pass
            return Response(data=None, success=True)
        
        except Exception as e:
            logger.error(f"Repository: Error getting signed URL: {str(e)}")
            return Response(data=str(e), success=False)

    async def update_schema_display_picture(self, schema_id: str, display_picture_url: str) -> Response:
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("schema").update({
                "display_picture": display_picture_url,
                "updated_at": "now()"
            }).eq("id", schema_id).execute()
            
            if not data_supabase.data:
                raise Exception("Erro ao atualizar display_picture do schema")
            
            return Response(data=data_supabase.data[0], success=True)
        
        except Exception as e:
            return Response(data=str(e), success=False)
    
    async def delete_schema(self, schema_id: str) -> Response:
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("schema").delete().eq("id", schema_id).execute()
            
            if not data_supabase.data:
                raise Exception("Erro ao excluir o schema")
            
            return Response(data=data_supabase.data[0], success=True)
            
        except Exception as e:
            return Response(data=str(e), success=False)
        
    async def update_schema_title(self, schema_id: str, new_title: str) -> Response:
        try:
            supabase = self._get_supabase_client()
            data_supabase = supabase.table("schema").update({
                "title": new_title,
                "updated_at": "now()"
            }).eq("id", schema_id).execute()
            
            if not data_supabase.data:
                raise Exception("Erro ao atualizar nome do schema")
            
            return Response(data=data_supabase.data[0], success=True)
        
        except Exception as e:
            return Response(data=str(e), success=False)

    async def get_users_by_schema(self, schema_id: str):
        try:
            supabase = self._get_supabase_client()
            data = supabase.from_('user_schema').select('id, user_id, user(id, name, email)').eq("schema_id", schema_id).execute()
            return Response(data=data.data or [], success=True)

        except Exception as e:
            return Response(data=str(e), success=False)