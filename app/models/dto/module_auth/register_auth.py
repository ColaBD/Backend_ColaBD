from pydantic import BaseModel

class RegisterAuth(BaseModel):
  name: str
  email: str
  password: str