from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.jwt import decode_access_token
from typing import Dict

# Security scheme for JWT Bearer token
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Authorization credentials containing the JWT token
        
    Returns:
        Dict containing user information (id, email)
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    token = credentials.credentials
    
    # Decode the JWT token
    result = decode_access_token(token)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return result.data


def get_current_user_id(current_user: Dict = Depends(get_current_user)) -> str:
    """
    Dependency to get only the current user's ID.
    
    Args:
        current_user: User data from get_current_user dependency
        
    Returns:
        str: User ID
    """
    return current_user["id"]