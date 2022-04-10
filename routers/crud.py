import datetime

from sqlalchemy.orm import Session, joinedload

from data import models, schemas as sc


def season_create(db: Session, user: models.User, start_date: datetime.date) -> models.Season:
    season = models.Season(year=start_date.year,
                           start_date=start_date,
                           owner_id=user.id)
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


def harvest_create(db: Session, user: models.User, season: models.Season,
                   data: sc.HarvestCreate) -> models.Harvest:
    # TODO list of employees when creating a harvest
    harvest = models.Harvest(
        date=data.date,
        price=data.price,
        fruit=data.fruit,
        harvested=data.harvested,
        season=season,
        owner_id=user.id
    )
    harvest.season = season
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

