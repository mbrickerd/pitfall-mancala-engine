from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
