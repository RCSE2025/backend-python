from typing import Any

from fastapi import HTTPException, status


class UserNotAdmin(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user is not admin",
        )


class CredentialsException(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class IncorrectPasswordException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserAlreadyExistsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )


class CodeNotExistsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Code not found")


class CodeExpiredException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code expired"
        )


class CodeIncorrectException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code incorrect",
        )


class EmailAlreadyVerifiedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified"
        )


class EmailNotVerifiedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email not verified"
        )


class UserNotRootException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail="User role not be root"
        )


class RepositoryUserAlreadyExistsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email exists in db",
        )


class UserNotFoundException(HTTPException):
    def __init__(self, search_param: Any) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with {search_param} not found",
        )
