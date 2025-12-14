from pydantic import BaseModel
from typing import Optional, Dict, Any


class CreateVersion(BaseModel):
    schema_id: str
    comment: Optional[str] = None
    data: Dict[str, Any]


