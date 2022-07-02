import decimal
from typing import Optional

from fastapi import Query

from .data.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def limit_offset(offset: int = 0, limit: int = 10):
    return {"offset": offset, "limit": limit}


async def after_before(
        after: Optional[str] = Query(None, min_length=10, max_length=10, regex=r"^[0-9]+(-[0-9]+)+$"),
        before: Optional[str] = Query(None, min_length=10, max_length=10, regex=r"^[0-9]+(-[0-9]+)+$")):
    return {"after": after, "before": before}


async def price_harvested_more_less(p_more: Optional[decimal.Decimal] = Query(None, gt=0),
                                    p_less: Optional[decimal.Decimal] = Query(None, le=100),
                                    h_more: Optional[decimal.Decimal] = Query(None, gt=0),
                                    h_less: Optional[decimal.Decimal] = Query(None, le=5000)):
    return {"p_more": p_more, "p_less": p_less, "h_more": h_more, "h_less": h_less}


async def order_by_query(order_by: Optional[str] = Query(default='', max_length=20),
                         order: Optional[str] = Query(default='desc', max_length=20)):
    return {'order_by': order_by, 'order': order}
