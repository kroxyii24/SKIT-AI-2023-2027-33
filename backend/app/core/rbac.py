"""
FastAPI dependencies for authentication and role-based access control.

Usage in a route:
    @router.get("/admin/stats")
    def stats(user: TokenPayload = Depends(require_role("admin"))):
        ...
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import BaseModel

from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class TokenPayload(BaseModel):
    sub: str  # user id
    role: str


def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
        return TokenPayload(sub=payload["sub"], role=payload["role"])
    except JWTError:
        raise credentials_exception


def require_role(*allowed_roles: str):
    """Dependency factory — restricts a route to specific roles."""

    def role_checker(user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {allowed_roles}",
            )
        return user

    return role_checker
