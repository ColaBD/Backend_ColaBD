from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from fastapi import UploadFile


class UpdateSchema(BaseModel):
    """DTO for updating a schema with cells data."""
    schema_id: str
    cells: List[Dict[str, Any]]
    display_picture: Optional[UploadFile] = None 