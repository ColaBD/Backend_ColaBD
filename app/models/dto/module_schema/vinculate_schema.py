from pydantic import BaseModel


class VinculateSchema(BaseModel):
    """DTO for vinculate a new schema."""
    schema_id: str
    user_email: str