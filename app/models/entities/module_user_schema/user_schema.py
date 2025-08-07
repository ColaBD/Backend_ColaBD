import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    """
    Many-to-many relationship table between User and Schema entities.
    Represents the association between users and schemas they have access to.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    schema_id: str