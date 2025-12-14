import uuid
from pydantic import BaseModel, Field


class SchemaVersion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    schema_id: str
    version_id: str


