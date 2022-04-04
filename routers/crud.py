import datetime

from sqlalchemy.orm import Session

from data import models


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
    seasons = db.query(models.Season).filter(models.Season.owner_id == user.id).all()
    seasons = [s.__dict__ for s in seasons]

    for season in seasons:
        season.pop("_sa_instance_state")
        try:
            harvests = []
            for harvest in season["harvests"]:
                harvest = harvest.__dict__
                harvest.pop("_sa_instance_state")
                harvests.append(harvest)
            season["harvests"] = harvests
        except KeyError:
            season["harvests"] = None
    seasons = {"seasons": seasons}
    return seasons


def season_get_year(db: Session, user: models.User, year: int) -> models.Season:
    season = db.query(models.Season)\
        .filter(models.Season.owner_id == user.id)\
        .filter(models.Season.year == year).first()
    return season
