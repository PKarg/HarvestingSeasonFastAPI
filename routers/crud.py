import datetime
import decimal
from typing import Optional, List

from fastapi import HTTPException, status
from sqlalchemy import extract
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from data import models as m, schemas as sc
from .validations import validate_date_qp, validate_date_in_bounds, validate_date_in_season_bounds, validate_fruit_qp


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


def season_update(db: Session, user: m.User, year: int,
                  data: sc.SeasonUpdate) -> m.Season:
    season = season_get(db=db, user=user, year=year)[0]
    if data.start_date:
        season.start_date = data.start_date
        season.year = data.start_date.year
    if data.end_date:
        season.end_date = data.end_date
    for e in season.employees:
        e: m.Employee
        validate_date_in_season_bounds(o_start=e.start_date, o_end=e.end_date,
                                       o_name='Employee', s_start=season.start_date,
                                       s_end=season.end_date)
    for h in season.harvests:
        h: m.Harvest
        validate_date_in_season_bounds(o_start=h.date, o_end=h.date,
                                       o_name='Employee', s_start=season.start_date,
                                       s_end=season.end_date)

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

    harvest_new = m.Harvest(
        date=data.date,
        price=data.price,
        fruit=data.fruit,
        harvested=data.harvested,
        season_id=season_m.id,
        owner_id=user.id
    )
    # TODO Change for crud method get_employees
    if data.employee_ids:
        harvest_new.employees = db.query(m.Employee)\
            .filter(m.Employee.id.in_(data.employee_ids))\
            .filter(m.Employee.season_id == season_m.id)\
            .all()

    db.add(harvest_new)
    db.commit()
    db.refresh(harvest_new)
    return harvest_new


def harvests_get(db: Session, user: m.User,
                 id: Optional[int] = None,
                 ids: Optional[List[int]] = None,
                 employee_id: Optional[int] = None,
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
    if id and not ids:
        harvests = harvests.filter(m.Harvest.id == id)
    if ids and not id:
        harvests = harvests.filter(m.Harvest.id.in_(ids))
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
        p_more = decimal.Decimal(p_more)
        harvests = harvests.filter(m.Harvest.price > p_more)
    if p_less:
        p_less = decimal.Decimal(p_less)
        harvests = harvests.filter(m.Harvest.price < p_less)
    if h_more:
        h_more = decimal.Decimal(h_more)
        harvests = harvests.filter(m.Harvest.harvested > h_more)
    if h_less:
        h_less = decimal.Decimal(h_less)
        harvests = harvests.filter(m.Harvest.harvested < h_less)
    if employee_id:
        employee_m: m.Employee = employees_get(db=db, user=user, id=employee_id)[0]
        harvest_ids = [h.id for h in employee_m.harvests]
        harvests = harvests.filter(m.Harvest.id.in_(harvest_ids))
    harvests = harvests.all()
    if not harvests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Couldn't find Harvest with specified parameters")
    return harvests


def harvest_update(db: Session, user: m.User, id: int,
                   data: sc.HarvestUpdate) -> m.Harvest:
    harvest: m.Harvest = harvests_get(db, user, id)[0]
    if data.date:
        for e in harvest.employees:
            e: m.Employee
            if not validate_date_in_bounds(bounds_start=e.start_date, bounds_end=e.end_date, start_date=data.date):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Given date {data.date} conflicts with Employee {e.id}")
    if data.fruit:
        harvest.fruit = data.fruit
        for w in harvest.workdays:
            w: m.Workday
            w.fruit = data.fruit
            db.add(w)
            db.commit()
    if data.harvested:
        harvested_in_workdays = 0
        for w in harvest.workdays:
            harvested_in_workdays += w.harvested
        if harvested_in_workdays > data.harvested:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Amt harvested {data.harvested} can't be lower than sum harvested in Workdays")
        harvest.harvested = data.harvested
    if data.price:
        harvest.price = data.price
    if data.employee_ids:
        employees: List[m.Employee] = employees_get(db=db, user=user, ids=data.employee_ids)
        for e in employees:
            if not validate_date_in_bounds(bounds_start=e.start_date, bounds_end=e.end_date, start_date=data.date):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Employee with id {e.id} can't be added to Harvest because of date discrepency")
            harvest.employees.append(e)
    db.add(harvest)
    db.commit()
    db.refresh(harvest)
    return harvest


# EMPLOYEES ======================================================================================
def employee_create(db: Session, user: m.User, year: int,
                    data: sc.EmployeeCreate) -> m.Employee:
    season_m: m.Season = season_get(db=db, user=user, year=year)[0]
    validate_date_in_season_bounds(o_name="Employee", o_start=data.start_date, o_end=data.end_date,
                                   s_start=season_m.start_date, s_end=season_m.end_date)

    employee_new = m.Employee(
        employer_id=user.id,
        name=data.name,
        season_id=season_m.id,
        start_date=data.start_date,
        end_date=data.end_date
    )
    # TODO change for crud method get_harvests
    if data.harvest_ids:
        employee_new.harvests = db.query(m.Harvest)\
            .filter(m.Harvest.id.in_(data.harvest_ids))\
            .filter(m.Harvest.season_id == season_m.id).all()

    db.add(employee_new)
    db.commit()
    db.refresh(employee_new)

    return employee_new


def employees_get(db: Session, user: m.User,
                  id: Optional[int] = None,
                  ids: Optional[List[int]] = None,
                  harvest_id: Optional[int] = None,
                  year: Optional[int] = None,
                  season_id: Optional[str] = None,
                  name: Optional[str] = None,
                  after: Optional[str] = None,
                  before: Optional[str] = None) -> List[m.Employee]:
    employees = db.query(m.Employee).filter(m.Employee.employer_id == user.id)
    if id and not ids:
        employees = employees.filter(m.Employee.id == id)
    if ids and not id:
        employees = employees.filter(m.Employee.id.in_(ids))
    if harvest_id:
        harvest: m.Harvest = harvests_get(db=db, user=user, id=harvest_id)[0]
        employee_ids = [e.id for e in harvest.employees]
        employees = employees.filter(m.Employee.id.in_(employee_ids))
    if season_id:
        try:
            season_id = int(season_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="season_id must be a number") from e
        employees = employees.filter(m.Employee.season_id == season_id)
    if year:
        employees = employees.filter(extract('year', m.Employee.start_date) == year)
    if name:
        employees = employees.filter(m.Employee.name == name)
    if after:
        after = validate_date_qp(after)
        employees = employees.filter(m.Employee.start_date > after)
    if before:
        before = validate_date_qp(before)
        employees = employees.filter(m.Employee.start_date < before)
    employees = employees.all()
    if not employees:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Couldn't find Employee with specified parameters")
    return employees


def employee_update(db: Session, user: m.User, id: int,
                    data: sc.EmployeeUpdate) -> m.Employee:
    employee: m.Employee = employees_get(db, user, id)[0]
    if data.harvests_ids:
        harvests: List[m.Harvest] = harvests_get(db=db, user=user, ids=data.harvests_ids)
        for h in harvests:
            h: m.Harvest
            if not validate_date_in_bounds(bounds_start=employee.start_date,
                                           bounds_end=employee.end_date,
                                           start_date=h.start_date):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Harvest {h.id} date incompatible with Employee timeframe")
            employee.harvests.append(h)
    if data.name:
        employee.name = data.name
    if data.start_date:
        for h in employee.harvests:
            if not validate_date_in_bounds(bounds_start=employee.start_date,
                                           bounds_end=employee.end_date,
                                           start_date=h.start_date):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Dates exclude harvest {h.id}")
            employee.start_date = data.start_date
            if data.end_date:
                employee.end_date = data.end_date

    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


# EXPENSES ======================================================================================

def expense_create(db: Session, year: int, user: m.User,
                   data: sc.ExpenseCreate) -> m.Expense:
    season_m: m.Season = season_get(db=db, user=user, year=year)[0]
    validate_date_in_season_bounds(o_start=data.date, s_start=season_m.start_date,
                                   s_end=season_m.end_date, o_name="Expense")
    expense_new = m.Expense(
        type=data.type,
        amount=data.amount,
        date=data.date,
        season_id=season_m.id,
        owner_id=user.id
    )

    db.add(expense_new)
    db.commit()
    db.refresh(expense_new)

    return expense_new


def expenses_get(db: Session, user: m.User,
                 year: Optional[int] = None,
                 id: Optional[int] = None,
                 season_id: Optional[str] = None,
                 type: Optional[str] = None,
                 after: Optional[str] = None,
                 before: Optional[str] = None,
                 more: Optional[str] = None,
                 less: Optional[str] = None) -> List[m.Expense]:
    expenses = db.query(m.Expense).filter(m.Expense.owner_id == user.id)
    if id:
        expenses = expenses.filter(m.Expense.id == id)
    if year:
        expenses = expenses.filter(extract('year', m.Expense.date) == year)
    if season_id:
        try:
            season_id = int(season_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="season_id must be a number") from e
        expenses = expenses.filter(m.Expense.season_id == season_id)
    if type:
        expenses = expenses.filter(m.Expense.type == type)
    if after:
        after = validate_date_qp(after)
        expenses = expenses.filter(m.Expense.date > after)
    if before:
        before = validate_date_qp(before)
        expenses = expenses.filter(m.Expense.date < before)
    if more:
        more = decimal.Decimal(more)
        expenses = expenses.filter(m.Expense.amount > more)
    if less:
        less = decimal.Decimal(less)
        expenses = expenses.filter(m.Expense.amount < less)
    expenses = expenses.all()
    if not expenses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Couldn't find Expense with specified parameters")
    return expenses


def expense_update(db: Session, id: int, user: m.User,
                   data: sc.ExpenseUpdate) -> m.Expense:
    expense: m.Expense = expenses_get(db=db, user=user, id=id)[0]
    if data.amount:
        expense.amount = data.amount
    if data.date:
        validate_date_in_season_bounds(o_start=data.date, s_start=expense.season.start_date,
                                       o_end=data.date, s_end=expense.season.end_date,
                                       o_name="Expense")
        expense.date = data.date
    if data.type:
        expense.type = data.type
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


# WORKDAYS
def workday_create(db: Session,
                   user: m.User,
                   data: sc.WorkdayCreate,
                   h_id: Optional[int] = None,
                   e_id: Optional[int] = None) -> m.Workday:
    workday_new = m.Workday()
    workday_new.harvest_id = h_id or data.harvest_id
    workday_new.employee_id = e_id or data.employee_id
    workday_new.employer_id = user.id

    if not workday_new.harvest_id and workday_new.employee_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Both Employee and Harvest id are needed to create a Workday")

    harvest_m: m.Harvest = harvests_get(db=db, user=user, id=h_id)[0]
    employee_m: m.Employee = employees_get(db=db, user=user, id=e_id)[0]

    if harvest_m.season_id != employee_m.season_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Employee and Harvest must belong to the same season")

    if employee_m and employee_m not in harvest_m.employees:
        harvest_m.employees.append(employee_m)

    workday_new.fruit = harvest_m.fruit
    workday_new.harvested = data.harvested
    workday_new.pay_per_kg = data.pay_per_kg

    db.add(workday_new)
    db.commit()
    db.refresh(workday_new)
    return workday_new


def workdays_get(db: Session,
                 user: m.User,
                 id: Optional[int] = None,
                 h_id: Optional[int] = None,
                 e_id: Optional[int] = None,
                 fruit: Optional[str] = None,
                 h_more: Optional[str] = None,
                 h_less: Optional[str] = None,
                 p_more: Optional[str] = None,
                 p_less: Optional[str] = None) -> List[m.Workday]:
    workdays = db.query(m.Workday).filter(m.Workday.employer_id == user.id)
    if h_id:
        workdays = db.query(m.Workday).filter(m.Workday.harvest_id == h_id)
    if e_id:
        workdays = db.query(m.Workday).filter(m.Workday.employee_id == e_id)
    if p_more:
        p_more = decimal.Decimal(p_more)
        workdays = workdays.filter(m.Workday.pay_per_kg > p_more)
    if p_less:
        p_less = decimal.Decimal(p_less)
        workdays = workdays.filter(m.Workday.pay_per_kg < p_less)
    if h_more:
        h_more = decimal.Decimal(h_more)
        workdays = workdays.filter(m.Workday.harvested > h_more)
    if h_less:
        h_less = decimal.Decimal(h_less)
        workdays = workdays.filter(m.Workday.harvested < h_less)
    if fruit:
        workdays = workdays.filter(m.Workday.fruit == fruit)
    if id:
        workdays = workdays.filter(m.Workday.id == id)

    workdays = workdays.all()
    if not workdays:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Couldn't find Workday with specified parameters")
    return workdays


def workday_update(db: Session,
                   user: m.User,
                   id: int,
                   data: sc.WorkdayUpdate) -> m.Workday:
    workday: m.Workday = workdays_get(db=db, user=user, id=id)[0]
    if data.harvested:
        workday.harvested = data.harvested
    if data.pay_per_kg:
        workday.pay_per_kg = data.pay_per_kg

    if data.employee_id and not data.harvest_id:
        employee_m: m.Employee = employees_get(db=db, user=user, id=data.employee_id)[0]
        harvest_date = workday.harvest.date
        if not validate_date_in_bounds(start_date=harvest_date,
                                       bounds_start=employee_m.start_date,
                                       bounds_end=employee_m.end_date):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Harvest and Employee dates not compatible")
        else:
            workday.employee_id = data.employee_id

    if data.harvest_id and not data.employee_id:
        harvest_m: m.Harvest = harvests_get(db=db, user=user, id=data.harvest_id)[0]
        employee_start = workday.employee.start_date
        employee_end = workday.employee.end_date
        if not validate_date_in_bounds(start_date=harvest_m.date, bounds_start=employee_start, bounds_end=employee_end):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Harvest and Employee dates not compatible")
        workday.harvest_id = data.harvest_id
        workday.fruit = harvest_m.fruit

    if data.harvest_id and data.employee_id:
        employee_m: m.Employee = employees_get(db=db, user=user, id=data.employee_id)[0]
        harvest_m: m.Harvest = harvests_get(db=db, user=user, id=data.harvest_id)[0]
        if not validate_date_in_bounds(start_date=harvest_m.date,
                                       bounds_start=employee_m.start_date,
                                       bounds_end=employee_m.end_date):
            print(harvest_m.date)
            print(employee_m.start_date)
            print(employee_m.end_date)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Harvest and Employee dates not compatible")
        workday.harvest_id = data.harvest_id
        workday.employee_id = data.employee_id
        workday.fruit = harvest_m.fruit

    db.add(workday)
    db.commit()
    db.refresh(workday)
    return workday
