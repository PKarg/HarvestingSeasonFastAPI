import datetime
import decimal
import decimal as dec
from typing import Optional, List

from fastapi import HTTPException, status
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
    price: dec.Decimal = Field(ge=0.5, le=100)
    harvested: dec.Decimal = Field(ge=1, le=5000)
    date: datetime.date
    fruit: models.Fruit

    @validator("harvested", pre=True, always=True)
    def check_decimals_harvested_harvest(cls, harvested: dec.Decimal):
        if dec.Decimal(harvested).same_quantum(dec.Decimal("1.0")):
            harvested = harvested
        else:
            harvested = dec.Decimal(harvested).quantize(dec.Decimal("1.0"))
        return harvested

    @validator("price", pre=True, always=True)
    def check_decimals_price(cls, price: dec.Decimal):
        if dec.Decimal(price).same_quantum(dec.Decimal("1.0")):
            price = price
        else:
            price = dec.Decimal(price).quantize(dec.Decimal("1.0"))
        return price


class HarvestCreate(HarvestBase):
    employee_ids: Optional[List[int]] = None


class HarvestResponseBase(HarvestBase):
    id: int
    season_id: int


class HarvestResponse(HarvestResponseBase):
    owner_id: int

    class Config:
        orm_mode = True


class HarvestReplace(HarvestCreate):
    pass


# Inheriting validators for decimal values
class HarvestUpdate(HarvestBase):
    fruit: Optional[str] = None
    harvested: Optional[decimal.Decimal] = Field(default=None, ge=1, le=5000)
    date: Optional[datetime.date] = None
    price: Optional[decimal.Decimal] = Field(default=None, ge=0.5, le=100)
    employee_ids: Optional[List[int]] = None

    class Config:
        orm_mode = True


# EMPLOYEES -----------------------
class EmployeeBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    start_date: datetime.date


class EmployeeCreate(EmployeeBase):
    end_date: Optional[datetime.date]
    harvest_ids: Optional[List[int]] = None


class EmployeeReplace(EmployeeCreate):
    season_id: int
    harvest_ids: List[int]


class EmployeeUpdate(EmployeeBase):
    name: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    harvests_ids: Optional[List[int]] = None


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
    harvested: decimal.Decimal = Field(ge=3, le=500)
    pay_per_kg: decimal.Decimal = Field(ge=1.5, le=10)

    @validator("harvested", pre=True, always=True)
    def check_decimals_harvested_workday(cls, harvested: dec.Decimal):
        if dec.Decimal(harvested).same_quantum(dec.Decimal("1.0")):
            harvested = harvested
        else:
            harvested = dec.Decimal(harvested).quantize(dec.Decimal("1.0"))
        return harvested

    @validator("pay_per_kg", pre=True, always=True)
    def check_decimals_price(cls, pay_per_kg: dec.Decimal):
        if dec.Decimal(pay_per_kg).same_quantum(dec.Decimal("1.0")):
            pay_per_kg = pay_per_kg
        else:
            pay_per_kg = dec.Decimal(pay_per_kg).quantize(dec.Decimal("1.0"))
        return pay_per_kg


class WorkdayUpdate(WorkdayCreate):
    employee_id: Optional[int] = None
    harvest_id: Optional[int] = None
    harvested: Optional[decimal.Decimal] = Field(default=None, ge=3, le=500)
    pay_per_kg: Optional[decimal.Decimal] = Field(default=None, ge=1.5, le=10)


class WorkdayResponse(WorkdayCreate):
    id: int
    employer_id: int
    fruit: str

    class Config:
        orm_mode = True


# RESPONSES WITH SUB-COLLECTIONS ======================================================
class HarvestResponseEmployees(HarvestResponse):
    employees: List[EmployeeResponse]

    class Config:
        orm_mode = True


class EmployeeResponseHarvests(EmployeeResponse):
    harvests: List[HarvestResponse]

    class Config:
        orm_mode = True


class HarvestResponseALL(HarvestResponse):
    employees: List[EmployeeResponse]
    workdays: List[WorkdayResponse]

    class Config:
        orm_mode = True


class EmployeeResponseALL(EmployeeResponse):
    harvests: List[HarvestResponse]
    workdays: List[WorkdayResponse]

    class Config:
        orm_mode = True


# EXPENSES ===============================================================
class ExpenseCreate(BaseModel):
    type: str
    date: datetime.date
    amount: decimal.Decimal = Field(ge=10, le=100000)

    @validator("amount", pre=True, always=True)
    def check_decimals_expense(cls, amount: dec.Decimal):
        if dec.Decimal(amount).same_quantum(dec.Decimal("1.0")):
            amount = amount
        else:
            amount = dec.Decimal(amount).quantize(dec.Decimal("1.0"))
        return amount


class ExpenseReplace(ExpenseCreate):
    season_id: int


class ExpenseUpdate(ExpenseCreate):
    type: Optional[str]
    date: Optional[datetime.date]
    amount: Optional[decimal.Decimal] = Field(default=None, ge=10, le=100000)


class ExpenseResponse(ExpenseCreate):
    id: int
    season_id: int
    owner_id: int

    class Config:
        orm_mode = True


# SEASONS ================================================================
class SeasonBase(BaseModel):
    start_date: datetime.date
    end_date: Optional[datetime.date] = None

    @validator("start_date", pre=True, always=True)
    def set_start_date(cls, start_date: Optional[datetime.date] = None):
        if start_date is None:
            start_date = datetime.datetime.now(datetime.timezone.utc).date()
        else:
            start_date = start_date
        return start_date


class SeasonUpdate(SeasonBase):
    pass


class SeasonResponse(SeasonBase):
    id: int
    year: int
    end_date: Optional[datetime.date] = None
    owner_id: int
    harvests: Optional[List[HarvestResponse]] = None
    employees: Optional[List[EmployeeResponse]] = None
    expenses: Optional[List[ExpenseResponse]] = None

    class Config:
        orm_mode = True
