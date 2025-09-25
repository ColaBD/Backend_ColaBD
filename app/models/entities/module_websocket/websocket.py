from typing import List, Dict, Any
from pydantic import BaseModel

class BaseTable(BaseModel):
    id: str

class CreateTable(BaseTable):
    attrs: Dict[str, Any]
    position: Dict[str, Any]
    size: Dict[str, Any]
    type: str

class DeleteTable(BaseTable):
    pass

class UpdateTable(BaseTable):
    attrs: Dict[str, Any]

class MoveTable(BaseTable):
    x: int
    y: int