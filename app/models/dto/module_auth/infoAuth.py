from datetime import datetime
from pydantic import BaseModel

class InfoAuth(BaseModel):
  access_token: str
  token_type: str
  exp: datetime