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
# HARVESTS -----------------------
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


class HarvestReplace(HarvestCreate):
    id: int
    season_id: int
    employees: List[int]


# Inheriting validators for decimal values
class HarvestUpdate(HarvestBase):
    fruit: Optional[str] = None
    harvested: Optional[decimal.Decimal] = None
    date: Optional[datetime.date] = None
    price: Optional[decimal.Decimal] = None
    season_id: Optional[int] = None
    employee_ids: Optional[List[int]] = None


class HarvestResponse(HarvestReplace):
    owner_id: int

    class Config:
        orm_mode = True


# EMPLOYEES -----------------------
class EmployeeBase(BaseModel):
    name: str
    start_date: datetime.date


class EmployeeCreate(EmployeeBase):
    harvest_ids: Optional[List[int]] = None


class EmployeeReplace(EmployeeCreate):
    season_id: int
    harvest_ids: List[int]


class EmployeeUpdate(EmployeeBase):
    name: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    harvests_ids: Optional[List[int]] = None
    season_id: Optional[int] = None


class EmployeeResponse(EmployeeBase):
    id: int
    season_id: int
    employer_id = int
    end_date: Optional[datetime.date] = None

    class Config:
        orm_mode = True


# WORKDAYS -----------------------
class WorkdayCreate(BaseModel):
    employee_id: Optional[int] = None
    harvest_id: Optional[int] = None
    fruit: str
    harvested: decimal.Decimal
    pay_per_kg: decimal.Decimal

    @validator("harvested", pre=True, always=True)
    def check_decimals_harvested(cls, harvested: dec.Decimal):
        if dec.Decimal(harvested).same_quantum(dec.Decimal("1.0")):
            harvested = harvested
            return harvested
        else:
            harvested = dec.Decimal(harvested).quantize(dec.Decimal("1.0"))
            return harvested

    @validator("pay_per_kg", pre=True, always=True)
    def check_decimals_price(cls, pay_per_kg: dec.Decimal):
        if dec.Decimal(pay_per_kg).same_quantum(dec.Decimal("1.0")):
            pay_per_kg = pay_per_kg
            return pay_per_kg
        else:
            pay_per_kg = dec.Decimal(pay_per_kg).quantize(dec.Decimal("1.0"))
            return pay_per_kg


class WorkdayReplace(WorkdayCreate):
    # TODO WorkdayReplace() seems redundant
    pass


class WorkdayUpdate(WorkdayCreate):
    employee_id: Optional[int] = None
    harvest_id: Optional[int] = None
    fruit: Optional[str] = None
    harvested: Optional[decimal.Decimal] = None
    pay_per_kg: Optional[decimal.Decimal] = None


# RESPONSES WITH SUB-COLLECTIONS ======================================================
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


class ExpenseReplace(ExpenseCreate):
    season_id: int


class ExpenseUpdate(ExpenseCreate):
    type: Optional[str]
    date: Optional[datetime.date]
    amount: Optional[decimal.Decimal]
    season_id: Optional[int]


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
