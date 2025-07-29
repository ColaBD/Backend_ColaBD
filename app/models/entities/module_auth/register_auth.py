from pydantic import BaseModel, EmailStr, field_validator
import re
import uuid

class RegisterAuth(BaseModel):
  name: str
  email: EmailStr
  password: str
  
  @field_validator('email')
  def validate_email(cls, email: EmailStr) -> EmailStr:
    if not re.search(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
      raise ValueError('Email must end with @example.com')
    
    return email