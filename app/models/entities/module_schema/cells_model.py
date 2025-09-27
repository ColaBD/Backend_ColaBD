from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any


class CellsModel(BaseModel):
    cells: list[dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now) 