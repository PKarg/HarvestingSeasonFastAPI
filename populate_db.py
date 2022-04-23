import datetime
import decimal
import random
import random as rand

from sqlalchemy.exc import IntegrityError

from data.database import SessionLocal
from data import models as m

from sqlalchemy.orm import Session

from routers import crud


def generate_random_seasons(start_year: int, end_year: int, user_id: int, db: Session) -> None:
    years = [i for i in range(start_year, end_year+1)]
    for year in years:
        start_date = datetime.date(year, random.randint(1, 12), random.randint(1, 28))
        end_date = datetime.date(year, random.randint(1, 12), random.randint(1, 28))
        while end_date < start_date:
            end_date = datetime.date(year, random.randint(1, 12), random.randint(1, 28))
        season = m.Season(
            year=year,
            start_date=start_date,
            end_date=end_date,
            owner_id=user_id
        )
        try:
            db.add(season)
            db.commit()
            db.refresh(season)
            print(season.owner)
        except IntegrityError:
            db.rollback()
            print(f"Season with year {year} already exists")


def generate_harvests_for_season(year: int, user_id: int, db: Session, num_of_harvests: int):
    fruits = ["strawberry", "cherry", "raspberry", "apple", "blackcurrant", "redcurrant", "apricot"]
    season_m: m.Season = db.query(m.Season).filter(m.Season.year == year)\
        .filter(m.Season.owner_id == user_id).first()
    for i in range(num_of_harvests):
        fruit = m.Fruit(fruits[random.randrange(0, len(fruits))])
        harvested = decimal.Decimal(random.randint(50, 2000) + random.randint(1, 9) / 10)
        price = decimal.Decimal(random.randint(1, 35) + random.randint(1, 9) / 10)
        date = datetime.date(year=year, month=random.randint(1, 12), day=random.randint(1, 28))
        while date > season_m.end_date or date < season_m.start_date:
            date = datetime.date(year=year, month=random.randint(1, 12), day=random.randint(1, 28))
        try:
            harvest = m.Harvest(
                fruit=fruit,
                harvested=harvested,
                date=date,
                price=price,
                season_id=season_m.id,
                owner_id=user_id
            )
            db.add(harvest)
            db.commit()
            db.refresh(harvest)
            print(harvest.__dict__)
        except IntegrityError as e:
            db.rollback()
            print(f"Couldn't create harvest with given parameters: "
                  f"{fruit, harvested, date, price, season_m.id, user_id}")
            print(e)


if __name__ == "__main__":
    db: Session = SessionLocal()
    # generate_random_seasons(2000, 2032, 1, db)
    # generate_harvests_for_season(2012, 1, db, 12)
