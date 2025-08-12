import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    schema_id: str