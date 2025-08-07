from fastapi import APIRouter, HTTPException, Depends

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
async def update_schema(update_data: UpdateSchema, current_user_id: str = Depends(get_current_user_id)):
    """Update a schema with cells data and save to MongoDB."""
    result = await service_schema.update_schema(update_data, current_user_id)
    
    if not result.success:
        http_exception(result, 400)
    
    return Response(data=result.data, success=True)


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
