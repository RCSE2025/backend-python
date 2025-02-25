import enum
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.users.exceptions import CredentialsException
from app.users.models import User
from app.users.schemas import TokenData


class TokenTypesEnum(enum.Enum):
    """Enum representing different token types."""

    access = "access"
    refresh = "refresh"
    password = "password"


def create_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Creates a JWT token.

    Args:
        data: The payload data for the token.
        expires_delta: The timedelta for token expiration. If None, defaults to 15 minutes.

    Returns:
        The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.app.SECRET_KEY, algorithm=settings.app.ALGORITHM
    )
    return encoded_jwt


def create_access_token(user: User) -> str:
    """Creates an access token for a user.

    Args:
        user: The user object.

    Returns:
        The encoded access token.
    """
    expires_delta = timedelta(minutes=settings.app.ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {
        "sub": user.id,
        "type": TokenTypesEnum.access.value,
    }  # Use enum value for type
    return create_token(data, expires_delta)


def create_refresh_token(
    user: User,
) -> str:
    """Creates a refresh token for a user.

    Args:
        user: The user object.

    Returns:
        The encoded refresh token.
    """
    data = {
        "sub": user.id,
        "type": TokenTypesEnum.refresh.value,
    }  # Use enum value for type
    expires_delta = timedelta(minutes=settings.app.REFRESH_TOKEN_EXPIRE_MINUTES)
    return create_token(data, expires_delta)


def create_password_refresh_token(
    user: User,
) -> str:
    """Creates a password refresh token for a user.

    Args:
        user: The user object.

    Returns:
        The encoded password refresh token.
    """
    data = {
        "sub": user.id,
        "type": TokenTypesEnum.password.value,
    }  # Use enum value for type
    expires_delta = timedelta(minutes=settings.app.REFRESH_PASSWORD_EXPIRE_MINUTES)
    return create_token(data, expires_delta)


def decode_token(token: str) -> dict:
    """Decodes a JWT token.

    Args:
        token: The JWT token.

    Returns:
        The decoded token payload.

    Raises:
        jwt.DecodeError: If the token cannot be decoded.
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is invalid.

    """
    return jwt.decode(
        token, settings.app.SECRET_KEY, algorithms=[settings.app.ALGORITHM]
    )


def verify_token(token: str, token_type: TokenTypesEnum) -> TokenData:
    """Verifies a JWT token and extracts user ID.

    Args:
        token: The JWT token.
        token_type: The expected type of the token.

    Returns:
        A TokenData object containing the user ID.

    Raises:
        CredentialsException: If the token is invalid, expired, or of the wrong type.
    """
    try:
        token = token.strip()
        payload = jwt.decode(
            token, settings.app.SECRET_KEY, algorithms=[settings.app.ALGORITHM]
        )
        if payload["type"] != token_type.value:
            raise CredentialsException(detail="Invalid token")
        user_id: str = payload.get("sub")
        if user_id is None:
            raise CredentialsException(detail="Invalid token payload")
        token_data = TokenData(user_id=user_id)
        return token_data
    except jwt.DecodeError:
        raise CredentialsException(detail="Could not decode token")
    except jwt.ExpiredSignatureError:
        raise CredentialsException(detail="Token expired")
    except jwt.InvalidTokenError:
        raise CredentialsException(detail="Invalid token")
    except KeyError:
        raise CredentialsException(detail="Invalid token payload")
