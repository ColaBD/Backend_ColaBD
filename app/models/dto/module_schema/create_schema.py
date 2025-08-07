from pydantic import BaseModel


class CreateSchema(BaseModel):
    """DTO for creating a new schema."""
    title: str