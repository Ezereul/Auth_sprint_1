from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy import Select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.requests import PageParams
from src.schemas.responses import PagedResponseSchema

T = TypeVar("T")


async def _stmt_count(session: AsyncSession, stmt: Select) -> int:
    """Return count of records matches to statement."""
    count_stmt = stmt.with_only_columns(func.count()).order_by(None)
    return (await session.scalars(count_stmt)).first()


def _count_pages(elements_count: int, page_params: PageParams) -> int:
    """Return count of pages for pagination."""
    return (elements_count - 1) // page_params.size + 1


async def paginate(
    session: AsyncSession, stmt: Select, page_params: PageParams, response_schema: BaseModel
) -> PagedResponseSchema[T]:
    """
    Paginate query.

    :param session: A database session.
    :param stmt: A SELECT statement to paginate.
    :param page_params: A PageParams, containing parameters for current page.
    :param response_schema: A schema of element, contained on page.
    """
    records_total = await _stmt_count(session, stmt)
    pages_total = _count_pages(records_total, page_params)

    if page_params.page > pages_total:
        raise ValueError('Page number is greater than total count (%s > %s)' % (page_params.page, pages_total))

    paginated_query = stmt.offset((page_params.page - 1) * page_params.size).limit(page_params.size)
    data = (await session.scalars(paginated_query)).all()

    return PagedResponseSchema(
        first=1,
        last=pages_total,
        items=[response_schema.from_orm(item) for item in data],
        next=page_params.page + 1 if page_params.page < pages_total else None,
        prev=page_params.page - 1 if page_params.page > 1 else None,
        **page_params.model_dump(),
    )
