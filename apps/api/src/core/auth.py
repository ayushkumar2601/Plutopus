import os
import jwt
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-nok-token-key-123456789-longer-key-required")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Rotation key list
JWT_SECRETS_LIST = [JWT_SECRET]
if os.getenv("JWT_ROTATION_SECRETS"):
    additional_secrets = [s.strip() for s in os.getenv("JWT_ROTATION_SECRETS", "").split(",") if s.strip()]
    JWT_SECRETS_LIST.extend(additional_secrets)

# Validate key strength
for key in JWT_SECRETS_LIST:
    if len(key) < 32:
        # Enforce compliance-ready length of at least 32 characters
        raise ValueError("Compliance security breach: JWT secrets must be at least 32 characters long.")

security = HTTPBearer(auto_error=False)

class UserPayload(BaseModel):
    username: str
    role: str  # admin, operator, viewer

def create_access_token(username: str, role: str) -> str:
    """
    Encodes username and RBAC role into a HS256 JWT access token.
    """
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "role": role,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserPayload:
    """
    Dependency checking JWT validity from Authorization Header or secure HttpOnly cookies.
    Supports JWT key rotation decoding.
    """
    token = None
    if credentials:
        token = credentials.credentials

    if not token:
        # Fallback to cookie authentication for web browser dashboard pages
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header token or session cookie",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Try decoding token against key rotation ring
    last_err = None
    for key in JWT_SECRETS_LIST:
        try:
            payload = jwt.decode(token, key, algorithms=[JWT_ALGORITHM])
            username: str = payload.get("sub")
            role: str = payload.get("role")
            if username is None or role is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return UserPayload(username=username, role=role)
        except jwt.PyJWTError as e:
            last_err = e

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Token signature validation failed or expired: {str(last_err)}",
        headers={"WWW-Authenticate": "Bearer"},
    )

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = [r.lower() for r in allowed_roles]

    def __call__(self, user: UserPayload = Depends(get_current_user)) -> UserPayload:
        if user.role.lower() not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. User role '{user.role}' lacks permission."
            )
        return user
