import datetime
import decimal
import decimal as dec
import json
from typing import Optional, List

from pydantic import BaseModel, Field, validator

from . import models


# TODO add docs examples to schemas

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


# HARVESTS && EMPLOYEES && WORKDAYS ================================================================
# TODO add workday schemas

class WorkdayCreate(BaseModel):
    pass


class HarvestBase(BaseModel):
    price: dec.Decimal
    harvested: dec.Decimal
    date: datetime.date
    fruit: models.Fruit

    @validator("harvested", pre=True, always=True)
    def check_decimals_harvested(cls, harvested: dec.Decimal):
        if dec.Decimal(harvested).same_quantum(dec.Decimal("1.0")):
            harvested = harvested
            return harvested
        else:
            harvested = dec.Decimal(harvested).quantize(dec.Decimal("1.0"))
            return harvested

    @validator("price", pre=True, always=True)
    def check_decimals_price(cls, price: dec.Decimal):
        if dec.Decimal(price).same_quantum(dec.Decimal("1.0")):
            price = price
            return price
        else:
            price = dec.Decimal(price).quantize(dec.Decimal("1.0"))
            return price


class HarvestCreate(HarvestBase):
    employees: Optional[List[int]] = None
    workdays: Optional[List[WorkdayCreate]] = None


class HarvestUpdate(HarvestCreate):
    id: int
    season_id: int


class HarvestResponse(HarvestUpdate):
    owner_id: int

    class Config:
        orm_mode = True


class EmployeeBase(BaseModel):
    name: str
    start_date: datetime.date


class EmployeeCreate(EmployeeBase):
    harvests: Optional[List[int]]


class EmployeeResponse(EmployeeBase):
    id: int
    season_id: int
    employer_id = int
    end_date: Optional[datetime.date] = None

    class Config:
        orm_mode = True


class HarvestResponseEmployees(HarvestResponse):
    employees: Optional[List[EmployeeResponse]] = None

    class Config:
        orm_mode = True


class EmployeeResponseHarvests(EmployeeResponse):
    harvests: Optional[List[HarvestResponse]] = None

    class Config:
        orm_mode = True


# EXPENSES ===============================================================
class ExpenseCreate(BaseModel):
    type: str
    date: datetime.date
    amount: decimal.Decimal

    @validator("amount", pre=True, always=True)
    def check_decimals_expense(cls, amount: dec.Decimal):
        if dec.Decimal(amount).same_quantum(dec.Decimal("1.0")):
            amount = amount
            return amount
        else:
            amount = dec.Decimal(amount).quantize(dec.Decimal("1.0"))
            return amount


class ExpenseResponse(ExpenseCreate):
    id: int
    season_id: int

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
        return start_date


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
    harvests: Optional[List[HarvestResponse]] = None
    employees: Optional[List[EmployeeResponse]] = None
    expenses: Optional[List[ExpenseResponse]] = None

    class Config:
        orm_mode = True
