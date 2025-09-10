from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.jwt import decode_access_token
from typing import Dict

# Security scheme for JWT Bearer token
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    return get_token_decoded(credentials.credentials)
    

def get_current_user_WS(user_token: str) -> str:
    return get_token_decoded(user_token)

def get_token_decoded(token: str):
    result = decode_access_token(token)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return result.data

def get_current_user_id(current_user: Dict = Depends(get_current_user)) -> str:
    return current_user["id"]