from pydantic import BaseModel
from typing import List, Dict, Any


class UpdateSchema(BaseModel):
    schema_id: str
    cells: List[Dict[str, Any]] 