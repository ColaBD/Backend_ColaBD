from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any


class CellsModel(BaseModel):
    cells: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now) 