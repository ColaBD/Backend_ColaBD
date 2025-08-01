from datetime import datetime
from pydantic import BaseModel

from app.models.dto.module_user.user import User

class InfoAuth(BaseModel):
  access_token: str
  exp: datetime
  token_type: str
  user_info: User