from pydantic import BaseModel
from typing import List, Dict, Any


class UpdateSchema(BaseModel):
    """DTO for updating a schema with cells data."""
    schema_id: str
    cells: List[Dict[str, Any]] 