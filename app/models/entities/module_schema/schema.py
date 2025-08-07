import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class Schema(BaseModel):
  id: str = Field(default_factory=lambda: str(uuid.uuid4()))
  title: str
  display_picture: str
  database_model: Optional[str] = None  # Optional field to store MongoDB ObjectId
  created_at: datetime = Field(default_factory=datetime.now)
  updated_at: datetime = Field(default_factory=datetime.now)