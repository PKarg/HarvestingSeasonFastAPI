import datetime
import json
from typing import Optional, List

from pydantic import BaseModel, Field


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
    start_date = datetime.date


class SeasonUpdate(SeasonBase):
    end_date = datetime.date
