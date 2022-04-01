import datetime

from sqlalchemy.orm import Session

from data import models


def create_season(db: Session, user: models.User, start_date: datetime.date) -> models.Season:
    season: models.Season = models.Season(year=start_date.year,
                                          start_date=start_date,
                                          owner_id=user.id)
    season.owner = user
    db.add(season)
    db.commit()
    db.refresh(season)
    return season
