from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')  # Generic type for the data payload

class BaseResult(BaseModel, Generic[T]):
    """
    Base response model for all API endpoints.
    """
    success: bool
    message: Optional[str] = None
    data: Optional[T] = None
    error_code: Optional[int] = None

    @classmethod
    def success_response(cls, data: T = None, message: str = None) -> "BaseResult[T]":
        """Helper method to create a success response."""
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_response(cls, message: str, error_code: int = None) -> "BaseResult[T]":
        """Helper method to create an error response."""
        return cls(success=False, message=message, error_code=error_code)