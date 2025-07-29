import uuid
from pydantic import BaseModel, Field, field_validator

import re

class User(BaseModel):
  id: str = Field(default_factory=lambda: str(uuid.uuid4()))
  name: str
  email: str
  password: str
  
  @field_validator('email')
  @classmethod
  def validate_email(cls, email: str) -> str:
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
      raise ValueError('O e-mail deve ser informado seguindo o padrão exemplo@exemplo.com')
    
    return email