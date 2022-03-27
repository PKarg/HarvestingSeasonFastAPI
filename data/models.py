from enum import Enum

from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DATE, DateTime, DECIMAL
from sqlalchemy.orm import relationship

from .database import Base


class Fruit(str, Enum):
    strawberry = "strawberry"
    cherry = "cherry"
    raspberry = "raspberry"
    apple = "apple"
    blackcurrant = "blackcurrant"
    redcurrant = "redcurrant"
    apricot = "apricot"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    seasons = relationship("Season", back_populates="owner")


class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    start_date = Column(DATE, nullable=False)
    end_date = Column(DATE)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="seasons")

    harvests = relationship("Harvest", back_populates="season")
    employees = relationship("Employee", back_populates="season")
    expenses = relationship("Expense", back_populates="season")


class Harvest(Base):
    __tablename__ = "harvests"

    id = Column(Integer, primary_key=True, index=True)
    fruit = Column(String, nullable=False)
    date = Column(DATE, nullable=False)
    harvested = Column(DECIMAL(1), nullable=False)
    price = Column(DECIMAL(1), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"))

    season = relationship("Season", back_populates="harvests")

    employees = relationship("Employee", back_populates="harvest")
    workdays = relationship("Workday", back_populates="harvest")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    date = Column(DATE, nullable=False)
    amount = Column(DECIMAL(1), nullable=False)
    season_id = Column(ForeignKey("seasons.id"))

    season = relationship("Season", back_populates="expenses")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"))
    start_date = Column(DATE, nullable=False)
    end_date = Column(DATE)

    season = relationship("Season", back_populates="employees")

    workdays = relationship("Workday", back_populates="employee")


class Workday(Base):
    __tablename__ = "workdays"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    harvest_id = Column(Integer, ForeignKey("harvests.id"))
    fruit = Column(String, nullable=False)
    harvested = Column(DECIMAL(1))
    pay_per_kg = Column(DECIMAL(1))

    employee = relationship("Employee", back_populates="workdays")
    harvest = relationship("Harvest", back_populates="workdays")
