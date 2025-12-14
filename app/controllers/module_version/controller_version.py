from fastapi import APIRouter, HTTPException, Depends
import logging

logger = logging.getLogger(__name__)

from app.models.dto.compartilhado.response import Response
from app.models.dto.module_version.create_version import CreateVersion
from app.services.module_version.service_version import ServiceVersion
from app.core.auth import get_current_user_id

router = APIRouter(
    prefix="/versions",
    tags=["versions"],
    responses={404: {"description": "Not found"}},
)

# Initialize service
service_version = ServiceVersion()


def http_exception(result, status=500):
    raise HTTPException(detail=result.data, status_code=status)


@router.post("", response_model=Response)
async def save_version(version_data: CreateVersion, current_user_id: str = Depends(get_current_user_id)):
    """Save a new version for a schema."""
    result = await service_version.create_version(version_data, current_user_id)
    
    if not result.success:
        http_exception(result, 400)
    
    return Response(data=result.data, success=True)


@router.get("/schema/{schema_id}", response_model=Response)
async def get_versions_by_schema(schema_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Get all versions for a specific schema."""
    result = await service_version.get_versions_by_schema(schema_id, current_user_id)
    
    if not result.success:
        http_exception(result, 403 if "negado" in result.data else 500)
    
    return Response(data=result.data, success=True)


