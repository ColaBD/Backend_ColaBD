from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

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


class Lock(BaseModel):
    """Modelo para rastrear locks de elementos em tempo real."""
    element_id: str
    user_id: str
    schema_id: str
    locked_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    
    class Config:
        arbitrary_types_allowed = True
    
    def is_expired(self) -> bool:
        """Verifica se o lock expirou."""
        return datetime.utcnow() > self.expires_at
    
    def refresh(self, ttl_seconds: int = 30) -> None:
        """Renova o lock com novo tempo de expiração."""
        self.locked_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)


class LockResponse(BaseModel):
    """Response para operações de lock."""
    success: bool
    element_id: str
    user_id: str
    locked_by_user: bool
    message: str
    expires_at: datetime | None = None


class LockedElement(BaseModel):
    """Informação de elemento bloqueado para enviar ao cliente."""
    element_id: str
    user_id: str
    locked_by_user: bool
    expires_at: datetime | None = None