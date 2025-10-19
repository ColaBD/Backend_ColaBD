from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class BaseElement(BaseModel):
    id: str
    class Config: #classe própria do pydntic que permite configurar o comportamento do modelo
        extra = "ignore"  # Ignora campos extras não definidos no modelo
class Position(BaseModel):
    x: int
    y: int

class Size(BaseModel):
    width: int
    height: int

class CreateTable(BaseElement):
    type: str = "standard.Rectangle"
    position: Position
    size: Size
    attrs: Dict[str, Any] 
    
class UpdateTable(BaseElement):
    attrs: Dict[str, Any]  

class MoveTable(BaseElement):
    position: Position

class DeleteTable(BaseElement):
    pass

class TableLabelAttrs(BaseModel):
    text: str
    fontSize: Optional[int] = None
    fontWeight: Optional[str] = None
    fill: Optional[str] = None

# class RowNameAttr(BaseModel):
#     text: str
#     fontSize: Optional[int] = None
#     fill: Optional[str] = None

# class RowTypeAttr(BaseModel):
#     text: str
#     fontSize: Optional[int] = None
#     fill: Optional[str] = None


# class RowMetaAttr(BaseModel):
#     pk: bool
#     fk: bool

class TableAttrs(BaseModel):
    label: TableLabelAttrs
    rows: Dict[str, Any] = {}  

class LinkEnd(BaseModel):
    id: str

class LinkLabelText(BaseModel):
    text: str
    fontSize: Optional[int] = None
    fontWeight: Optional[str] = None
    fill: Optional[str] = None

class TextUpdateLinkLabelAttrs(BaseElement):
    text: str 
    
class LinkLabelRect(BaseModel):
    fill: Optional[str] = None
    stroke: Optional[str] = None
    strokeWidth: Optional[int] = None
    rx: Optional[int] = None
    ry: Optional[int] = None

class LinkLabelAttrs(BaseModel):
    text: Optional[LinkLabelText] = None
    rect: Optional[LinkLabelRect] = None

class Label(BaseModel):
    attrs: LinkLabelAttrs
    position: Optional[float] = None

class LinkAttrs(BaseModel):
    connection: Optional[Dict[str, Any]] = Field(None, alias=".connection")
    marker_source: Optional[Dict[str, Any]] = Field(None, alias=".marker-source")
    marker_target: Optional[Dict[str, Any]] = Field(None, alias=".marker-target")

class LinkTable(BaseElement):
    type: str = "link"
    source: LinkEnd
    target: LinkEnd
    labels: list[Label] = []
    attrs: LinkAttrs
    
class SchemaUpdates(BaseModel):
    cells: list[dict[str, Any]] = Field(default_factory=list)
    task: Any | None = None