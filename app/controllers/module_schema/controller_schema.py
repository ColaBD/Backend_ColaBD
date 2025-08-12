from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile
from typing import Optional, List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

from app.models.dto.compartilhado.response import Response
from app.models.dto.module_schema.create_schema import CreateSchema
from app.models.dto.module_schema.update_schema import UpdateSchema
from app.services.module_schema.service_schema import ServiceSchema
from app.core.auth import get_current_user_id

router = APIRouter(
    prefix="/schemas",
    tags=["schemas"],
    responses={404: {"description": "Not found"}},
)

# Initialize service
service_schema = ServiceSchema()


def http_exception(result, status=500):
    """Helper function to raise HTTP exceptions."""
    raise HTTPException(detail=result.data, status_code=status)


@router.get("/", response_model=Response)
async def get_all_schemas(current_user_id: str = Depends(get_current_user_id)):
    """Get all schemas for the authenticated user."""
    result = await service_schema.get_schemas_by_user(current_user_id)
    
    if not result.success:
        http_exception(result, 500)
    
    return Response(data=result.data, success=True)


@router.post("/", response_model=Response)
async def create_schema(schema_data: CreateSchema, current_user_id: str = Depends(get_current_user_id)):
    """Create a new schema and associate it with the authenticated user."""
    result = await service_schema.create_schema(schema_data, current_user_id)
    
    if not result.success:
        http_exception(result, 400)
    
    return Response(data=result.data, success=True)


@router.put("/", response_model=Response)
async def update_schema(
    schema_id: str = Form(...),
    cells: str = Form(...),  # JSON string of cells data
    display_picture: Optional[UploadFile] = File(None),
    current_user_id: str = Depends(get_current_user_id)
):
    """Update a schema with cells data and save to MongoDB. Supports image upload via multipart form data."""
    try:
        logger.info(f"Starting schema update for schema_id: {schema_id}, user_id: {current_user_id}")
        logger.info(f"Has display_picture: {display_picture is not None}")
        if display_picture:
            logger.info(f"Image details - filename: {display_picture.filename}, content_type: {display_picture.content_type}, size: {display_picture.size}")
        
        # Parse cells JSON string
        logger.info("Parsing cells JSON data...")
        cells_data = json.loads(cells)
        logger.info(f"Successfully parsed {len(cells_data)} cells")
        
        # Create UpdateSchema object manually since we're using Form data
        class UpdateSchemaData:
            def __init__(self, schema_id: str, cells: List[Dict[str, Any]]):
                self.schema_id = schema_id
                self.cells = cells
        
        update_data = UpdateSchemaData(schema_id, cells_data)
        
        # Call service with display_picture parameter
        logger.info("Calling service update_schema method...")
        result = await service_schema.update_schema(update_data, current_user_id, display_picture)
        
        if not result.success:
            logger.error(f"Service returned error: {result.data}")
            http_exception(result, 400)
        
        logger.info("Schema update completed successfully")
        return Response(data=result.data, success=True)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        raise HTTPException(status_code=400, detail="Formato JSON inválido para o campo 'cells'")
    except Exception as e:
        logger.error(f"Unexpected error in update_schema: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{schema_id}", response_model=Response)
async def get_schema_by_id(schema_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Get schema by ID with cells data from MongoDB."""
    result = await service_schema.get_schema_with_cells(schema_id, current_user_id)
    
    if not result.success:
        http_exception(result, 404)
    
    return Response(data=result.data, success=True)


@router.get("/user/{user_id}", response_model=Response)
async def get_schemas_by_user(user_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Get all schemas for a specific user (admin endpoint)."""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Acesso negado: você só pode acessar seus próprios schemas")
    
    result = await service_schema.get_schemas_by_user(user_id)
    
    if not result.success:
        http_exception(result, 404)
    
    return Response(data=result.data, success=True)


@router.post("/test-upload", response_model=Response)
async def test_upload(
    schema_id: str = Form(...),
    display_picture: Optional[UploadFile] = File(None),
    current_user_id: str = Depends(get_current_user_id)
):
    """Test endpoint to debug image upload issues."""
    try:
        logger.info(f"Test upload started for schema_id: {schema_id}")
        
        if not display_picture:
            return Response(data={"message": "No image provided"}, success=True)
        
        logger.info(f"Image details - filename: {display_picture.filename}, content_type: {display_picture.content_type}, size: {display_picture.size}")
        
        # Test just the upload part
        upload_result = await service_schema.repo_schema.upload_schema_image(schema_id, display_picture)
        
        if not upload_result.success:
            logger.error(f"Upload failed: {upload_result.data}")
            return Response(data=f"Upload failed: {upload_result.data}", success=False)
        
        logger.info("Upload successful")
        return Response(data={"message": "Upload test successful", "result": upload_result.data}, success=True)
        
    except Exception as e:
        logger.error(f"Test upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
