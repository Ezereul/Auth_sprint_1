from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class DetailResponse(BaseModel):
    detail: str


class PagedResponseSchema(BaseModel, Generic[T]):
    """Response schema for any paged API."""
    page: int
    size: int
    first: int
    last: int
    prev: int | None = None
    next: int | None = None
    items: list[T]
