from pydantic import BaseModel

class UpdateSchemaTitle(BaseModel):
    new_title: str