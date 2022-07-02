import datetime
import traceback
from typing import Optional

from fastapi import HTTPException
from starlette import status
from project.data import models as m


def validate_date_qp(qp: str) -> datetime.date:
    try:
        return datetime.date.fromisoformat(qp)
    except ValueError as e:
        print(e)
        print(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=str(e)) from e


def validate_fruit_qp(qp: str) -> m.Fruit:
    try:
        fruit = m.Fruit(qp.lower())
        return fruit.value
    except ValueError as e:
        print(e)
        print(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=str(e)) from e


def validate_date_in_season_bounds(o_start: datetime.date, s_start: datetime.date, o_name: str,
                                   o_end: Optional[datetime.date] = None, s_end: Optional[datetime.date] = None) -> None:
    """
    Check if dates related to given object are in bounds allowed by given season dates.
    If dates are out of bounds raises exception taking into account given object name

    :param o_start: start (or only) date for given object
    :param s_start: start date for given season
    :param o_name: name of object (for example "Harvest")
    :param o_end: end date for given object
    :param s_end: end date for given season
    :return:
    """
    if s_end:
        if o_end and not (s_start <= o_start <= o_end <= s_end):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=f"{o_name} start and end dates have to be between season start and end: {s_start}:{s_end}")
        elif not (s_start <= o_start <= s_end):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=f"{o_name} start date has to be between season start and end: {s_start}:{s_end}")
    elif o_end and not (s_start <= o_start <= o_end):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"{o_name} start date must be before employee end date: {s_end},"
                                   f" and both can't be before season start date: {s_start}")
    elif not s_start <= o_start:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"{o_name} start date can't be before season start date: {s_start}")


def validate_date_in_bounds(start_date: datetime.date,
                            bounds_start: datetime.date,
                            end_date: Optional[datetime.date] = None,
                            bounds_end: Optional[datetime.date] = None) -> bool:
    """
    Universal version of date validation similar to valdiate_date_in_season_bounds()

    :param start_date: object start date
    :param bounds_start: bounds start
    :param end_date: object end date (optional)
    :param bounds_end: bounds end
    :return: bool
    """
    if bounds_end:
        if end_date and not (bounds_start <= start_date <= end_date <= bounds_end):
            print("1")
            return False
        elif not (bounds_start <= start_date <= bounds_end):
            print("2")
            return False
        else:
            return True
    elif end_date and not (bounds_start <= start_date <= end_date):
        print("3")
        return False
    elif not bounds_start <= start_date:
        print("4")
        return False
    else:
        return True


def validate_order_by(order_by: str, order: str, orders: dict):
    if not isinstance(orders, dict):
        raise TypeError(f"Orders must be passed as dict, not {type(orders)}")
    for k in orders.keys():
        if not isinstance(k, str):
            raise TypeError(f"Each ordering parameter must be of type str, not {type(k)}")
    if not orders:
        raise ValueError("'orders' can't be empty")
    if order not in ('desc', 'asc'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Order can only be desc, asc, not {order}")
    if order_by not in orders.keys():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Seasons can be ordered only by {orders.keys()}, not {order_by}")
