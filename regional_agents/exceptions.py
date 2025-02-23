from fastapi import HTTPException, status


class UserNotAgentException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is not agent"
        )


class RegionalAgentNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regional agent not found",
        )


class UserNotApprovedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User regional agent not approved",
        )
