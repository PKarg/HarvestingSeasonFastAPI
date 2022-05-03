from enum import Enum

from sqlalchemy import Column, Integer, ForeignKey, String,\
    Boolean, DATE, DECIMAL, Table, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


harvests_employees_asoc_tab = Table('association', Base.metadata,
                                    Column('harvest_id',
                                           ForeignKey('harvests.id'),
                                           primary_key=True),
                                    Column('employee_id',
                                           ForeignKey('employees.id'),
                                           primary_key=True))


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

    UniqueConstraint(year, owner_id, name='u_yo')

    owner = relationship("User", back_populates="seasons")

    harvests = relationship("Harvest", back_populates="season", cascade="all, delete")
    employees = relationship("Employee", back_populates="season", cascade="all, delete")
    expenses = relationship("Expense", back_populates="season", cascade="all, delete")


class Harvest(Base):
    __tablename__ = "harvests"

    id = Column(Integer, primary_key=True, index=True)
    fruit = Column(String, nullable=False)
    harvested = Column(DECIMAL(5, 1), nullable=False)
    date = Column(DATE, nullable=False)
    price = Column(DECIMAL(5, 1), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    UniqueConstraint(date, fruit, name='u_df')

    season = relationship("Season", back_populates="harvests")

    employees = relationship("Employee",
                             secondary=harvests_employees_asoc_tab,
                             back_populates="harvests")

    workdays = relationship("Workday", back_populates="harvest", cascade="all, delete")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    date = Column(DATE, nullable=False)
    amount = Column(DECIMAL(6, 1), nullable=False)
    season_id = Column(ForeignKey("seasons.id"))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

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

    harvests = relationship("Harvest",
                            secondary=harvests_employees_asoc_tab,
                            back_populates="employees")

    workdays = relationship("Workday", back_populates="employee", cascade="all, delete")


class Workday(Base):
    __tablename__ = "workdays"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    harvest_id = Column(Integer, ForeignKey("harvests.id"))
    harvested = Column(DECIMAL(5, 1))
    pay_per_kg = Column(DECIMAL(5, 1))
    fruit = Column(String(30), nullable=False)
    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    employee = relationship("Employee", back_populates="workdays")
    harvest = relationship("Harvest", back_populates="workdays")
