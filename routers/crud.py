import datetime
import decimal
import traceback
from typing import Optional, List

from fastapi import HTTPException, status
from sqlalchemy import extract
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from data import models as m, schemas as sc


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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"{o_name} start and end dates have to be between season start and end")
        elif not (s_start <= o_start <= s_end):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"{o_name} start date has to be between season start and end")
    elif o_end and not s_start <= o_start <= o_end:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{o_name} start date must be before employee end date, and both can't be before season start date")
    elif not s_start <= o_start:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{o_name} start date can't be before season start date")


# SEASONS ===============================================================================================
def season_create(db: Session, user: m.User,
                  start_date: datetime.date,
                  end_date: Optional[datetime.date] = None) -> m.Season:
    try:
        season = m.Season(year=start_date.year,
                          start_date=start_date,
                          owner_id=user.id)
        if end_date and end_date.year == start_date.year:
            season.end_date = end_date
        elif end_date:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dates need to have the sane year")
        season.owner = user
        db.add(season)
        db.commit()
        db.refresh(season)
        return season
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Season with given year already exists") from e


def season_get(db: Session, user: m.User,
               year: Optional[int] = None,
               after: Optional[str] = None,
               before: Optional[str] = None,
               limit: Optional[str] = None,
               offset: Optional[str] = None) -> List[m.Season]:
    seasons: db.query = db.query(m.Season)\
        .options(
        joinedload(m.Season.employees),
        joinedload(m.Season.harvests),
        joinedload(m.Season.expenses))\
        .filter(m.Season.owner_id == user.id)
    if year:
        seasons = seasons.filter(m.Season.year == year)
    if after:
        after = validate_date_qp(after)
        seasons = seasons.filter(m.Season.start_date > after)
    if before:
        before = validate_date_qp(before)
        seasons = seasons.filter(m.Season.start_date > before)
    if offset:
        offset = int(offset)
        seasons = seasons.offset(offset)
    if limit:
        limit = int(limit)
        seasons = seasons.limit(limit)

    seasons = seasons.all()
    if not seasons:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Couldn't find Seasons with specified parameters")

    return seasons


def season_update(db: Session, season: m.Season,
                  new_start_date: Optional[datetime.date] = None,
                  new_end_date: Optional[datetime.date] = None) -> m.Season:
    if new_start_date:
        season.start_date = new_start_date
        season.year = new_end_date.year
    if new_end_date:
        season.end_date = new_end_date

    db.add(season)
    db.commit()
    db.refresh(season)
    return season


# HARVESTS ======================================================================================
def harvest_create(db: Session, user: m.User, year: int,
                   data: sc.HarvestCreate) -> m.Harvest:

    season_m: m.Season = season_get(db, user, year)[0]
    validate_date_in_season_bounds(o_name="Harvest", o_start=data.date, s_start=season_m.start_date,
                                   s_end=season_m.end_date, o_end=data.date)

    harvest_m_new = m.Harvest(
        date=data.date,
        price=data.price,
        fruit=data.fruit,
        harvested=data.harvested,
        season_id=season_m.id,
        owner_id=user.id
    )
    if data.employee_ids:
        harvest_m_new.employees = db.query(m.Employee)\
            .filter(m.Employee.id.in_(data.employee_ids))\
            .filter(m.Employee.season_id == season_m.id)\
            .all()

    db.add(harvest_m_new)
    db.commit()
    db.refresh(harvest_m_new)
    return harvest_m_new


def harvest_get(db: Session, user: m.User,
                id: Optional[int] = None,
                year: Optional[int] = None,
                season_id: Optional[int] = None,
                after: Optional[str] = None,
                before: Optional[str] = None,
                fruit: Optional[str] = None,
                p_more: Optional[str] = None,
                p_less: Optional[str] = None,
                h_more: Optional[str] = None,
                h_less: Optional[str] = None) -> List[m.Harvest]:
    # TODO add order by options
    harvests = db.query(m.Harvest).filter(m.Harvest.owner_id == user.id)
    if id:
        harvests = harvests.filter(m.Harvest.id == id)
    if year:
        harvests = harvests.filter(extract('year', m.Harvest.date) == year)
    if season_id:
        harvests = harvests.filter(m.Harvest.season_id == season_id)
    if after:
        after = validate_date_qp(after)
        harvests = harvests.filter(m.Harvest.date > after)
    if before:
        before = validate_date_qp(before)
        harvests = harvests.filter(m.Harvest.date < before)
    if fruit:
        fruit = validate_fruit_qp(fruit)
        harvests = harvests.filter(m.Harvest.fruit == fruit)
    if p_more:
        p_more = int(p_more)
        harvests = harvests.filter(m.Harvest.price > p_more)
    if p_less:
        p_less = int(p_less)
        harvests = harvests.filter(m.Harvest.price < p_less)
    if h_more:
        h_more = int(h_more)
        harvests = harvests.filter(m.Harvest.harvested > h_more)
    if h_less:
        h_less = int(h_less)
        harvests = harvests.filter(m.Harvest.harvested < h_less)
    harvests = harvests.all()
    if not harvests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Couldn't find Harvest with specified parameters")
    return harvests


# EMPLOYEES ======================================================================================
def employee_create(db: Session, user: m.User, year: int,
                    data: sc.EmployeeCreate) -> m.Employee:
    season_m: m.Season = season_get(db=db, user=user, year=year)[0]
    validate_date_in_season_bounds(o_name="Employee", o_start=data.start_date, o_end=data.end_date,
                                   s_start=season_m.start_date, s_end=season_m.end_date)

    employee_m_new = m.Employee(
        employer_id=user.id,
        name=data.name,
        season_id=season_m.id,
        start_date=data.start_date,
        end_date=data.end_date
    )
    if data.harvest_ids:
        employee_m_new.harvests = db.query(m.Harvest)\
            .filter(m.Harvest.id.in_(data.harvest_ids))\
            .filter(m.Harvest.season_id == season_m.id).all()

    db.add(employee_m_new)
    db.commit()
    db.refresh(employee_m_new)

    return employee_m_new


def employee_get(db: Session, user: m.User,
                 id: Optional[int] = None,
                 season_id: Optional[int] = None):
    employees = db.query(m.Employee).filter(m.Employee.employer_id == user.id)
    if id:
        employees = employees.filter(m.Employee.id == id)
    if season_id:
        employees = employees.filter(m.Employee.season_id)
    employees = employees.all()
    if not employees:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Couldn't find Employee with specified parameters")
    return employees


# EXPENSES ======================================================================================

def expense_create(db: Session, year: int, user: m.User,
                   data: sc.ExpenseCreate) -> m.Expense:
    season_m: m.Season = season_get(db=db, user=user, year=year)[0]
    validate_date_in_season_bounds(o_start=data.date, s_start=season_m.start_date,
                                   s_end=season_m.end_date, o_name="Expense")
    expense_m_new = m.Expense(
        type=data.type,
        amount=data.amount,
        date=data.date,
        season_id=season_m.id,
        owner_id=user.id
    )

    db.add(expense_m_new)
    db.commit()
    db.refresh(expense_m_new)

    return expense_m_new


# WORKDAYS
def workday_create(db: Session,
                   user: m.User,
                   data: sc.WorkdayCreate,
                   h_id: Optional[int] = None,
                   e_id: Optional[int] = None) -> m.Workday:
    workday_m_new = m.Workday()
    workday_m_new.harvest_id = h_id or data.harvest_id
    workday_m_new.employee_id = e_id or data.employee_id
    workday_m_new.employer_id = user.id

    if not workday_m_new.harvest_id and workday_m_new.employee_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Both Employee and Harvest id are needed to create a Workday")

    harvest_m: m.Harvest = harvest_get(db=db, user=user, id=h_id)[0]
    employee_m: m.Employee = employee_get(db=db, user=user, id=e_id)[0]

    if harvest_m.season_id != employee_m.season_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Employee and Harvest must belong to the same season")

    if employee_m and employee_m not in harvest_m.employees:
        harvest_m.employees.append(employee_m)

    workday_m_new.fruit = harvest_m.fruit
    workday_m_new.harvested = data.harvested
    workday_m_new.pay_per_kg = data.pay_per_kg

    db.add(workday_m_new)
    db.commit()
    db.refresh(workday_m_new)
    return workday_m_new
