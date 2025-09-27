from typing import Any
from pydantic import BaseModel

class BaseTable(BaseModel):
    id: str

class CreateTable(BaseTable):
    attrs: dict[str, Any]
    position: dict[str, Any]
    size: dict[str, Any]
    type: str

class DeleteTable(BaseTable):
    pass

class UpdateTable(BaseTable):
    attrs: dict[str, Any]

class MoveTable(BaseTable):
    x: int
    y: int