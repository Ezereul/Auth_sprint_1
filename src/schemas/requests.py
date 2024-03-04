from typing import Annotated

from fastapi import Query
from pydantic import BaseModel


class PageParams(BaseModel):
    """Request query params for paginated API."""

    page: Annotated[int, Query(description='Page number', ge=1)] = 1
    size: Annotated[int, Query(description='Page size', ge=1, le=100)] = 10
