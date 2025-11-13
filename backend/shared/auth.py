"""JWT authentication and authorization helpers."""
from typing import Callable, Iterable, List

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from .config import settings


security = HTTPBearer(auto_error=True)


class User(BaseModel):
    sub: str
    roles: List[str]


class TokenError(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED) -> None:
        super().__init__(status_code=status_code, detail=detail)


def decode_jwt(token: str) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub"]},
        )
    except jwt.ExpiredSignatureError as exc:  # pragma: no cover - pass-through
        raise TokenError("Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("Invalid token") from exc

    roles = payload.get("roles") or []
    if not isinstance(roles, Iterable):
        roles = []

    return User(sub=str(payload.get("sub")), roles=list(roles))


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    token = credentials.credentials
    return decode_jwt(token)


def require_roles(*allowed_roles: str) -> Callable[[User], User]:
    if not allowed_roles:
        raise ValueError("At least one role is required")

    def dependency(user: User = Depends(get_current_user)) -> User:
        if not any(role in user.roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return dependency


__all__ = ["User", "decode_jwt", "get_current_user", "require_roles"]
