from pydantic import BaseModel

class LoginAuth(BaseModel):
  email: str
  password: str