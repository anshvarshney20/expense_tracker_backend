from typing import Any, Optional


class AppError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: Optional[str] = None,
        data: Any = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.data = data
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", data: Any = None):
        super().__init__(message, status_code=404, error_code="NOT_FOUND", data=data)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized access", data: Any = None):
        super().__init__(message, status_code=401, error_code="UNAUTHORIZED", data=data)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Permission denied", data: Any = None):
        super().__init__(message, status_code=403, error_code="FORBIDDEN", data=data)


class ValidationError(AppError):
    def __init__(self, message: str = "Validation error", data: Any = None):
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR", data=data)


class InternalServerError(AppError):
    def __init__(self, message: str = "Internal server error", data: Any = None):
        super().__init__(
            message, status_code=500, error_code="INTERNAL_SERVER_ERROR", data=data
        )
