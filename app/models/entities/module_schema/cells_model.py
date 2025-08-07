from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any


class CellsModel(BaseModel):
    """Model for storing cells data in MongoDB."""
    cells: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now) 