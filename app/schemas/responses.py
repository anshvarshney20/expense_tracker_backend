from typing import Generic, Optional, TypeVar, Any
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[Any] = None
    message: str


class SuccessResponse(APIResponse[T]):
    success: bool = True
    message: str = "Operation successful"


class ErrorResponse(APIResponse[None]):
    success: bool = False
    message: str = "An error occurred"
