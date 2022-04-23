import datetime
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from data import models, schemas as sc


def season_create(db: Session, user: models.User,
                  start_date: datetime.date,
                  end_date: Optional[datetime.date] = None) -> models.Season:
    season = models.Season(year=start_date.year,
                           start_date=start_date,
                           owner_id=user.id)
    if end_date:
        season.end_date = end_date
    season.owner = user
    db.add(season)
    db.commit()
    db.refresh(season)
    return season


def season_get_all(db: Session, user: models.User) -> list[models.Season]:
    seasons: list[models.Season] = db.query(models.Season)\
        .options(
        joinedload(models.Season.employees),
        joinedload(models.Season.harvests))\
        .filter(models.Season.owner_id == user.id).all()
    return seasons


def season_get_by_year(db: Session, user: models.User, year: int) -> models.Season:
    season = db.query(models.Season)\
        .options(
        joinedload(models.Season.employees),
        joinedload(models.Season.harvests))\
        .filter(models.Season.owner_id == user.id)\
        .filter(models.Season.year == year).first()
    return season


def season_update(db: Session, season: models.Season,
                  new_start_date: Optional[datetime.date] = None,
                  new_end_date: Optional[datetime.date] = None) -> models.Season:
    if new_start_date:
        season.start_date = new_start_date
        season.year = new_end_date.year
    if new_end_date:
        season.end_date = new_end_date

    db.add(season)
    db.commit()
    db.refresh(season)
    return season


def harvest_create(db: Session, user: models.User, season_id: int,
                   data: sc.HarvestCreate) -> models.Harvest:

    harvest = models.Harvest(
        date=data.date,
        price=data.price,
        fruit=data.fruit,
        harvested=data.harvested,
        season_id=season_id,
        owner_id=user.id
    )
    if data.employees:
        harvest.employees = db.query(models.Employee)\
            .filter(models.Employee.id.in_(data.employees))\
            .filter(models.Employee.season_id == season_id)\
            .all()

    db.add(harvest)
    db.commit()
    db.refresh(harvest)
    return harvest


def employee_create(db: Session, user: models.User, season: models.Season,
                    data: sc.EmployeeCreate) -> models.Employee:
    employee = models.Employee(
        employer_id=user.id,
        name=data.name,
        season_id=season.id,
        start_date=data.start_date
    )
    employee.season = season
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

