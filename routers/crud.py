import datetime
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from data import models as m, schemas as sc


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
               after: Optional[datetime.date] = None,
               before: Optional[datetime.date] = None) -> list[m.Season]:
    seasons: db.query = db.query(m.Season)\
        .options(
        joinedload(m.Season.employees),
        joinedload(m.Season.harvests))\
        .filter(m.Season.owner_id == user.id)
    if after:
        seasons = seasons.filter(m.Season.start_date > after)
    if before:
        seasons = seasons.filter(m.Season.start_date < after)
    return seasons.all()


def season_get_by_year(db: Session, user: m.User, year: int) -> m.Season:
    season = db.query(m.Season)\
        .options(
        joinedload(m.Season.employees),
        joinedload(m.Season.harvests))\
        .filter(m.Season.owner_id == user.id)\
        .filter(m.Season.year == year).first()
    return season


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
                year: Optional[int] = None,
                season_id: Optional[int] = None,
                ):
    pass


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
