import datetime
import random
import traceback

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from project.data.database import SessionLocal
from project.data import models as m
from project.additional import ApiLogger


def generate_constrained_sum(n, total):
    dividers = sorted(random.sample(range(1, total), n-1))
    return [a - b for a, b in zip(dividers + [total], [0] + dividers)]


def generate_workdays(harvests: list[m.Harvest], user_id):
    workdays_to_generate = sum([len(h.employees) for h in harvests])
    i = 1
    print(f"Generating Workdays ============================================================")
    dates = [h.date for h in harvests]
    for harvest in harvests:
        try:
            if len(harvest.employees) == 0:
                print(f"Skipping harvest {harvest.date}  - no employees found")
                continue
            print(dates)
            harvested_per_employee = generate_constrained_sum(len(harvest.employees),
                                                              int(harvest.harvested))

            for employee, harvested in zip(harvest.employees, harvested_per_employee):
                print(f"Generating Workday for harvest {harvest.date} - {i} out of {workdays_to_generate}")
                print(employee.id, harvested)
                workday = m.Workday()
                workday.harvest_id = harvest.id
                workday.employer_id = user_id
                workday.employee_id = employee.id
                workday.fruit = harvest.fruit
                workday.harvested = harvested if harvested <= 500 else 500
                workday.pay_per_kg = harvest.price / 3
                db.add(workday)
                db.commit()
                i += 1
        except IntegrityError:
            msg = "Integrity error while generating Workdays - ignoring faulty data"
            print(msg)
            ApiLogger.create_module_exception_log("populator", msg)
            db.rollback()


def generate_harvests(start_date: datetime.date, end_date: datetime.date,
                      n: int, season_id: int, user_id: int, db: Session):
    """EXECUTE AFTER generate_employees"""
    fruits = ['strawberry', 'cherry', 'raspberry', 'apricot']
    days_between = (end_date - start_date).days
    harvests = []
    i = 1
    print(f"Generating Harvests ============================================================")
    for _ in range(n):
        try:
            print(f"Generating Harvest for year {start_date.year} - {i} out of {n}")
            i += 1
            harvest = m.Harvest()
            harvest.fruit = fruits[random.randrange(0, len(fruits))]
            harvest.date = start_date + datetime.timedelta(days=random.randint(0, days_between))
            harvest.harvested = random.randint(500, 5000)
            harvest.price = random.randint(5, 25)
            harvest.season_id = season_id
            harvest.owner_id = user_id
            harvest.employees = db.query(m.Employee).filter(m.Employee.employer_id == user_id)\
                .filter(m.Employee.start_date <= harvest.date)\
                .filter(m.Employee.end_date >= harvest.date).all()

            db.add(harvest)
            db.commit()
            db.refresh(harvest)
            harvests.append(harvest)
            print(f"Harvest date: {harvest.date}")

        except IntegrityError:
            msg = "Integrity error while generating Harvests - ignoring faulty data"
            print(msg)
            ApiLogger.create_module_exception_log("populator", msg)
            db.rollback()
    return harvests


def generate_employees(start_date: datetime.date,
                       end_date: datetime.date,
                       n: int,
                       season_id: int,
                       user_id: int,
                       db: Session):
    names = ["Nayeli Le", "Johan Oliver", "Jeffery Fisher", "Theresa Taylor",
             "Atticus Gay", "Cara Baldwin", "Caden Madden", "Liberty Bowen",
             "Elijah Dennis", "Valentin Montoya", "Estrella Wyatt", "Audrey Mckay"
             "Clara Robinson", "Charlize Hanson", "Izayah Bridges", "Liberty Bowen"]
    i = 1
    print(f"Generating Employees ============================================================")
    for _ in range(n):
        try:
            print(f"Generating Employee for year {start_date.year} - {i} out of {n}")
            i += 1
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
        except IntegrityError:
            msg = "Integrity error while generating Employees - ignoring faulty data"
            print(msg)
            ApiLogger.create_module_exception_log("populator", msg)
            db.rollback()


def generate_expenses(n: int, season_id: int, user_id: int,
                      start_date: datetime.date, end_date: datetime.date,
                      db: Session):
    types = ["general", "pesticides", "herbicides", "fungicides", "fuel", "maintenance"]
    days_between = (end_date - start_date).days
    i = 1
    print(f"Generating Expenses ============================================================")
    for _ in range(n):
        try:
            print(f"Generating Expense for year {start_date.year} - {i} out of {n}")
            i += 1
            expense = m.Expense()
            expense.season_id = season_id
            expense.owner_id = user_id
            expense.type = types[random.randrange(0, len(types))]
            expense.date = start_date + datetime.timedelta(days=random.randint(0, days_between))
            expense.amount = random.randint(150, 10000)
            db.add(expense)
            db.commit()
        except IntegrityError:
            msg = "Integrity error while generating Expenses - ignoring faulty data"
            print(msg)
            ApiLogger.create_module_exception_log("populator", msg)
            db.rollback()


def generate_seasons(start_year: int, end_year: int, user_id: int, db: Session):
    i = 1
    print("Starting db population =========================================================")
    try:
        for year in range(start_year, end_year + 1):
            print(f"Generating Season for year {year} - {i} out of {end_year + 1 - start_year}")
            i += 1
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

            generate_expenses(n=random.randint(6, 24), season_id=season.id, user_id=user_id,
                              start_date=season.start_date, end_date=season.end_date,
                              db=db)
            generate_employees(start_date=season.start_date, end_date=season.end_date,
                               season_id=season.id, user_id=user_id, db=db,
                               n=random.randint(4, 16))
            harvests = generate_harvests(db=db, season_id=season.id, start_date=season.start_date,
                                         end_date=season.end_date, user_id=user_id, n=random.randint(12, 48))
            generate_workdays(harvests=harvests, user_id=user_id)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("Error occured during generation of dummy data - cleaning db")
        ApiLogger.create_module_exception_log("populator", traceback.format_exc())
        db.rollback()
        db.query(m.Season).filter(m.Season.owner_id == user_id).delete()
        db.commit()


if __name__ == "__main__":
    db: Session = SessionLocal()
    generate_seasons(2121, 2123, 1, db)
