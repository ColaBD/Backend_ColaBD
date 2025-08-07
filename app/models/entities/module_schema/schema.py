import uuid
from datetime import datetime
from pydantic import BaseModel, Field

class Schema(BaseModel):
  id: str = Field(default_factory=lambda: str(uuid.uuid4()))
  title: str
  display_picture: str
  database_model: uuid.UUID
  created_at: datetime = Field(default_factory=datetime.now)
  updated_at: datetime = Field(default_factory=datetime.now)