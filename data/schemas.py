import datetime
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


# SEASONS================================================================
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

    class Config:
        orm_mode = True
