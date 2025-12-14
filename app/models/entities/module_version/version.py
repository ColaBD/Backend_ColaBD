import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class Version(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tag: int
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str
    comment: Optional[str] = None
    data: Dict[str, Any]


