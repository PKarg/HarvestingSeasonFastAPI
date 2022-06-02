import datetime
import decimal
import random
import math

from sqlalchemy.exc import IntegrityError

from project.data.database import SessionLocal
from project.data import models as m

from sqlalchemy.orm import Session


def generate_constrained_sum(n, total):
    dividers = sorted(random.sample(range(1, total), n-1))
    return [a - b for a, b in zip(dividers + [total], [0] + dividers)]


def generate_workdays(harvests: list[m.Harvest], user_id):
    for harvest in harvests:
        harvested_per_employee = generate_constrained_sum(len(harvest.employees),
                                                          harvest.harvested)
        for employee, harvested in zip(harvest.employees, harvested_per_employee):
            workday = m.Workday()
            workday.harvest_id = harvest.id
            workday.employer_id = user_id
            workday.employee_id = employee.id
            workday.fruit = harvest.fruit
            workday.harvested = harvested
            workday.pay_per_kg = harvest.price / 3
            db.add(workday)
            db.commit()


def generate_harvests(start_date: datetime.date, end_date: datetime.date,
                      num_of_seasons, season_id: int, user_id: int, db: Session):
    """EXECUTE AFTER generate_employees"""
    fruits = ['strawberry', 'cherry', 'raspberry', 'apricot']
    harvest = m.Harvest()
    days_between = (end_date - start_date).days
    harvests = []
    for _ in range(num_of_seasons):
        harvest_date = start_date + datetime.timedelta(days=random.randint(0, days_between))
        harvest.fruit = fruits[random.randrange(0, len(fruits))]
        harvest.date = harvest_date
        harvest.harvested = random.randint(500, 5000)
        harvest.price = random.randint(5, 25)
        harvest.season_id = season_id
        harvest.owner_id = user_id
        harvest.employees = db.query(m.Employee).filter(m.Employee.employer_id == user_id).filter()

        db.add(harvest)
        db.commit()
        db.refresh(harvest)
        harvests.append(harvest)
    return harvests


def generate_employees(start_date: datetime.date,
                       end_date: datetime.date,
                       num_of_employees: int,
                       season_id: int,
                       user_id: int,
                       db: Session):
    names = ["Nayeli Le", "Johan Oliver", "Jeffery Fisher", "Theresa Taylor",
             "Atticus Gay", "Cara Baldwin", "Caden Madden", "Liberty Bowen",
             "Elijah Dennis", "Valentin Montoya", "Estrella Wyatt", "Audrey Mckay"
             "Clara Robinson", "Charlize Hanson", "Izayah Bridges", "Liberty Bowen"]
    for _ in range(num_of_employees):
        employee = m.Employee()
        random_days = random.randint(0, 15)
        employee.start_date = start_date + datetime.timedelta(days=random_days)
        employee.end_date = end_date - datetime.timedelta(days=random_days)
        employee.name = names[random.randrange(0, len(names))]
        employee.season_id = season_id
        employee.employer_id = user_id
        db.add(employee)
        db.commit()
        db.refresh(employee)


def generate_expenses(n: int, season_id: int, user_id: int,
                      start_date: datetime.date, end_date: datetime.date):
    types = ["general", "pesticides", "herbicides", "fungicides", "fuel", "maintenance"]
    days_between = (end_date - start_date).days
    for _ in range(n):
        expense = m.Expense()
        expense.season_id = season_id
        expense.owner_id = user_id
        expense.type = types[random.randrange(0, len(types))]
        expense.date = start_date + datetime.timedelta(days=random.randint(0, days_between))
        expense.amount = random.randint(150, 10000)
        db.add(expense)
        db.commit()


def generate_seasons(start_year: int, end_year: int, user_id: int, db: Session):
    for year in range(start_year, end_year + 1):
        season = m.Season()
        season.owner_id = user_id
        season.year = year
        season.start_date = datetime.date(year,
                                          random.randint(5, 6),
                                          random.randint(2, 30))
        season.end_date = datetime.date(year,
                                        random.randint(8, 10),
                                        random.randint(2, 30))
        db.add(season)
        db.commit()
        db.refresh(season)

        generate_expenses(random.randint(6, 24), season_id=season.id, user_id=user_id,
                          start_date=season.start_date, end_date=season.end_date)
        generate_employees()
        # TODO generate sub-objects for season
        #   - generate expenses
        #   - generate employees
        #   - generate harvests
        #   - generate workdays


if __name__ == "__main__":
    db: Session = SessionLocal()
    # TODO generate full seasons
