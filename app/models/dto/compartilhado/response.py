from pydantic import BaseModel
from typing import Any

class Response(BaseModel):
  data: Any
  status_code: int
  success: bool
