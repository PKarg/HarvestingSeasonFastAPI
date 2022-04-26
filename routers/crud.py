import datetime
import decimal
import traceback
from typing import Optional, List

from fastapi import HTTPException, status
from sqlalchemy import extract
from sqlalchemy.orm import Session, joinedload

from data import models as m, schemas as sc


def validate_date_qp(qp: str) -> datetime.date:
    try:
        date = datetime.date.fromisoformat(qp)
        return date
    except ValueError as e:
        print(e)
        print(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=str(e))


def validate_fruit_qp(qp: str) -> m.Fruit:
    try:
        fruit = m.Fruit(qp.lower())
        return fruit.value
    except ValueError as e:
        print(e)
        print(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=str(e))


def season_create(db: Session, user: m.User,
                  start_date: datetime.date,
                  end_date: Optional[datetime.date] = None) -> m.Season:
    season = m.Season(year=start_date.year,
                      start_date=start_date,
                      owner_id=user.id)
    if end_date:
        season.end_date = end_date
    season.owner = user
    db.add(season)
    db.commit()
    db.refresh(season)
    return season


def season_get(db: Session, user: m.User,
               year: Optional[int] = None,
               after: Optional[str] = None,
               before: Optional[str] = None) -> List[m.Season]:
    seasons: db.query = db.query(m.Season)\
        .options(
        joinedload(m.Season.employees),
        joinedload(m.Season.harvests))\
        .filter(m.Season.owner_id == user.id)
    if year:
        seasons = seasons.filter(m.Season.year == year)
    if after:
        after = validate_date_qp(after)
        seasons = seasons.filter(m.Season.start_date > after)
    if before:
        before = validate_date_qp(before)
        seasons = seasons.filter(m.Season.start_date > before)
    return seasons.all()


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


def harvest_create(db: Session, user: m.User, season_id: int,
                   data: sc.HarvestCreate) -> m.Harvest:

    harvest = m.Harvest(
        date=data.date,
        price=data.price,
        fruit=data.fruit,
        harvested=data.harvested,
        season_id=season_id,
        owner_id=user.id
    )
    if data.employees:
        harvest.employees = db.query(m.Employee)\
            .filter(m.Employee.id.in_(data.employees))\
            .filter(m.Employee.season_id == season_id)\
            .all()

    db.add(harvest)
    db.commit()
    db.refresh(harvest)
    return harvest


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
    return harvests.all()


def employee_create(db: Session, user: m.User, season: m.Season,
                    data: sc.EmployeeCreate) -> m.Employee:
    employee = m.Employee(
        employer_id=user.id,
        name=data.name,
        season_id=season.id,
        start_date=data.start_date
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def expense_create(db: Session, season: m.Season,
                   data: sc.ExpenseCreate) -> m.Expense:
    expense = m.Expense(
        type=data.type,
        date=data.date,
        amount=data.amount,
        season_id=season.id
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense
