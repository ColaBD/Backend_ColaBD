from pydantic import BaseModel
from typing import Any, Optional
from fastapi import UploadFile


class UpdateSchema(BaseModel):
    """DTO for updating a schema with cells data."""
    schema_id: str
    cells: list[dict[str, Any]]
    display_picture: Optional[UploadFile] = None 