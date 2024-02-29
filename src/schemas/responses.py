from typing import Generic, TypeVar

from pydantic import BaseModel, computed_field

T = TypeVar("T")


class DetailResponse(BaseModel):
    detail: str


class PagedResponseSchema(BaseModel, Generic[T]):
    """Response schema for any paged API."""

    page: int
    size: int
    first: int = 1
    last: int
    items: list[T]

    @computed_field
    @property
    def prev(self) -> int | None:
        return self.page - 1 if self.page > 1 else None

    @computed_field
    @property
    def next(self) -> int | None:
        return self.page + 1 if self.page < self.last else None
