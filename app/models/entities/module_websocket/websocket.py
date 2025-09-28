from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class BaseTable(BaseModel):
    id: str

class Position(BaseModel):
    x: int
    y: int

class Size(BaseModel):
    width: int
    height: int

class CreateTable(BaseTable):
    type: str = "standard.Rectangle"
    position: Position
    size: Size
    attrs: Dict[str, Any] 
    
class UpdateTable(BaseTable):
    attrs: Dict[str, Any]  

class MoveTable(BaseTable):
    position: Position

class DeleteTable(BaseTable):
    pass

class TableLabelAttrs(BaseModel):
    text: str
    fontSize: Optional[int] = None
    fontWeight: Optional[str] = None
    fill: Optional[str] = None

class RowNameAttr(BaseModel):
    text: str
    fontSize: Optional[int] = None
    fill: Optional[str] = None

class RowTypeAttr(BaseModel):
    text: str
    fontSize: Optional[int] = None
    fill: Optional[str] = None


class RowMetaAttr(BaseModel):
    pk: bool
    fk: bool

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
    position: Optional[int] = None

class LinkAttrs(BaseModel):
    connection: Optional[Dict[str, Any]] = None
    marker_source: Optional[Dict[str, Any]] = None
    marker_target: Optional[Dict[str, Any]] = None

class LinkRouter(BaseModel):
    name: str

class LinkConnector(BaseModel):
    name: str

class LinkTable(BaseTable):
    type: str = "link"
    source: LinkEnd
    target: LinkEnd
    router: Optional[LinkRouter] = None
    connector: Optional[LinkConnector] = None
    labels: list[Label] = []
    attrs: Optional[LinkAttrs] = None
    
class SchemaUpdates(BaseModel):
    cells: list[dict[str, Any]] = Field(default_factory=list)
    task: Any | None = None