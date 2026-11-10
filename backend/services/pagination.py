"""
pagination.py
Server-side pagination (DataTables style): the database does the work with
LIMIT/OFFSET, only one page travels to the browser.

Query parameters shared by every list endpoint:
    page       1-based page number            (default 1)
    page_size  rows per page, max MAX_PAGE_SIZE (default 25)
    q          free-text search (per endpoint)
    sort_by    one of the endpoint's sortable columns
    sort_dir   asc | desc

Response envelope: {"items": [...], "total": N, "page": P, "page_size": S, "pages": K}
where `total` is the number of rows matching the filters/search.
"""
from math import ceil
from typing import Dict, Generic, List, Literal, Optional, TypeVar

from fastapi import Query
from pydantic import BaseModel

MAX_PAGE_SIZE = 100
T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items:     List[T]
    total:     int
    page:      int
    page_size: int
    pages:     int


class PageParams:
    """FastAPI dependency that reads the pagination/sorting query parameters."""

    def __init__(
        self,
        page:      int = Query(1, ge=1),
        page_size: int = Query(25, ge=1, le=MAX_PAGE_SIZE),
        sort_by:   Optional[str] = None,
        sort_dir:  Optional[Literal["asc", "desc"]] = None,
    ):
        self.page      = page
        self.page_size = page_size
        self.sort_by   = sort_by
        self.sort_dir  = sort_dir


def paginate(
    query,
    params: PageParams,
    sortable: Dict[str, object],
    default_sort: str,
    default_dir: str,
    tiebreaker,
) -> dict:
    """
    Apply ORDER BY + LIMIT/OFFSET to `query` and return the page envelope.

    `sortable` maps the public column names to ORM columns (whitelist: unknown
    names fall back to `default_sort`, so clients can never sort by arbitrary SQL).
    `tiebreaker` (usually the primary key) keeps page boundaries stable.
    """
    sort_key  = params.sort_by if params.sort_by in sortable else default_sort
    direction = params.sort_dir or (default_dir if sort_key == default_sort else "asc")
    column    = sortable[sort_key]
    ordering  = column.asc() if direction == "asc" else column.desc()

    total = query.order_by(None).count()
    items = (
        query.order_by(ordering, tiebreaker.asc())
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
        .all()
    )
    return {
        "items":     items,
        "total":     total,
        "page":      params.page,
        "page_size": params.page_size,
        "pages":     max(1, ceil(total / params.page_size)),
    }
