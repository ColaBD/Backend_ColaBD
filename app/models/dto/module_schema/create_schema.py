from pydantic import BaseModel


class CreateSchema(BaseModel):
    title: str