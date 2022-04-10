import datetime
import decimal as dec
import json
from typing import Optional, List

from pydantic import BaseModel, Field, validator

from . import models


# USERS================================================================
class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


# SEASONS ================================================================
class SeasonBase(BaseModel):
    start_date: Optional[datetime.date]

    @validator("start_date", pre=True, always=True)
    def set_start_date(cls, start_date: Optional[datetime.date] = None):
        if start_date is None:
            start_date = datetime.datetime.utcnow().date()
        else:
            start_date = start_date
        return  start_date


class SeasonUpdate(SeasonBase):
    end_date: Optional[datetime.date]

    @validator("end_date", pre=True, always=True)
    def set_end_date(cls, end_date: Optional[datetime.date] = None):
        if end_date is None:
            end_date = datetime.datetime.utcnow().date()
        else:
            end_date = end_date
        return end_date


class SeasonResponse(SeasonBase):
    id: int
    year: int
    end_date: Optional[datetime.date]
    owner_id: int
    harvests: Optional[List[dict]]
    employees: Optional[List[dict]]

    class Config:
        orm_mode = True


# TODO update response model
class SeasonListResponse(BaseModel):
    seasons: list[SeasonResponse]

    class Config:
        orm_mode = True


# HARVESTS && EMPLOYEES && WORKDAYS ================================================================
class HarvestAssoc(BaseModel):
    id: int


class EmployeeAssoc(BaseModel):
    id: int


class HarvestCreate(BaseModel):
    # TODO list of workdays
    price: dec.Decimal
    harvested: dec.Decimal
    date: datetime.date
    fruit: models.Fruit

    employees: Optional[List[EmployeeAssoc]] = None

    @validator("price", pre=True, always=True)
    def check_decimals_price(cls, price: dec.Decimal):
        if dec.Decimal(price).same_quantum(dec.Decimal("1.0")):
            price = price
            return price
        else:
            price = dec.Decimal(price).quantize(dec.Decimal("1.0"))
            return price


class EmployeeCreate(BaseModel):
    name: str
    start_date: datetime.date


class HarvestResponse(HarvestCreate):
    id: int
    season_id: int


class EmployeeResponse(BaseModel):
    pass
