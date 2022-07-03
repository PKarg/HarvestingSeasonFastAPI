import decimal
import json
import os
from typing import List, Optional, Union

from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks
from starlette.responses import FileResponse

from project.auth import get_current_active_user
from project.data import models as m, schemas as sc
from project.dependencies import get_db, limit_offset, after_before, price_harvested_more_less, order_by_query
from . import crud
from ..additional import create_temp_csv, delete_temp_files
router = APIRouter(
    prefix="/seasons",
    tags=["seasons"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def seasons_post(season_data: sc.SeasonBase,
                 user: m.User = Depends(get_current_active_user),
                 db: Session = Depends(get_db)):
    return crud.season_create(db, user, season_data.start_date, season_data.end_date)


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[sc.SeasonResponse])
def seasons_get_all(user: m.User = Depends(get_current_active_user),
                    db: Session = Depends(get_db),
                    limit_offset_qp=Depends(limit_offset),
                    after_before_qp=Depends(after_before),
                    order_by_qp=Depends(order_by_query)):
    return crud.season_get(db=db, user=user, **after_before_qp,
                           **limit_offset_qp, **order_by_qp)


@router.get("/summary")
def report_multiple_seasons(background_tasks: BackgroundTasks,
                            user: m.User = Depends(get_current_active_user),
                            db: Session = Depends(get_db),
                            limit_offset_qp=Depends(limit_offset),
                            after_before_qp=Depends(after_before),
                            order_by_qp=Depends(order_by_query),
                            data_format: str = Query('json', min_length=3, max_length=4)):
    if data_format not in ('json', 'csv'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Data format must be 'json' or 'csv', not '{data_format}'")
    seasons = crud.season_get(db=db, user=user, **after_before_qp,
                              **limit_offset_qp, **order_by_qp)
    summaries = [{
            'id': s.id,
            'year': s.year,
            'start_date': s.start_date,
            'end_date': s.end_date,
            'fruits': s.fruits,
            'employees_n': len(s.employees),
            'best_employee': s.best_employee['name'],
            'harvests_n': len(s.harvests),
            'best_harvest': s.best_harvest['date'],
            'total_harvested_value': s.total_harvested_value,
            'total_employee_payments': s.total_employee_payments,
            'total_expenses_value': s.total_expenses_value,
            'net_profits': s.total_harvested_value - s.total_employee_payments - s.total_expenses_value
        } for s in seasons]

    if data_format == 'csv':
        filename = f"user_{user.username}_{user.id}_seasons"
        compressed_file, tmp_dir = create_temp_csv(data=summaries,
                                                   filename=filename,
                                                   column_names=[k for k in summaries[0].keys()])
        background_tasks.add_task(delete_temp_files, tmp_dir)
        return FileResponse(path=os.path.join(tmp_dir, compressed_file), filename=compressed_file,
                            media_type='application/zip')
    else:
        return summaries


@router.get("/{year}", status_code=status.HTTP_200_OK,
            response_model=sc.SeasonResponse)
def seasons_get_by_year(year: int,
                        user: m.User = Depends(get_current_active_user),
                        db: Session = Depends(get_db)):
    return crud.season_get(db, user, year)[0]


@router.patch("/{year}", status_code=status.HTTP_200_OK,
              response_model=sc.SeasonResponse)
def seasons_update(year: int, season_data: sc.SeasonUpdate,
                   user: m.User = Depends(get_current_active_user),
                   db: Session = Depends(get_db)):
    return crud.season_update(db=db, user=user, year=year, data=season_data)


@router.delete("/{year}", status_code=status.HTTP_200_OK)
def seasons_delete(year: int,
                   user: m.User = Depends(get_current_active_user),
                   db: Session = Depends(get_db)):
    season_m = crud.season_get(db, user, year)[0]
    db.delete(season_m)
    db.commit()


@router.post("/{year}/harvests", status_code=status.HTTP_201_CREATED,
             response_model=sc.HarvestResponseEmployees)
def harvests_post(year: int,
                  harvest_data: sc.HarvestCreate,
                  user: m.User = Depends(get_current_active_user),
                  db: Session = Depends(get_db)):
    return crud.harvest_create(db, user, year, harvest_data)


@router.get("/{year}/harvests", status_code=status.HTTP_200_OK,
            response_model=Union[List[sc.HarvestResponseExtended]])
def harvests_get(background_tasks: BackgroundTasks,
                 year: int,
                 user: m.User = Depends(get_current_active_user),
                 db: Session = Depends(get_db),
                 after_before_qp=Depends(after_before),
                 fruit: Optional[str] = Query(None, min_length=3, max_length=30),
                 price_harvested_qp=Depends(price_harvested_more_less),
                 order_by_qp=Depends(order_by_query),
                 limit_offset_qp=Depends(limit_offset),
                 data_format: Optional[str] = Query('json', min_length=3, max_length=4),
                 extended: Optional[bool] = Query(False)):
    harvests = crud.harvests_get(db, user, year=year,
                                 fruit=fruit, **price_harvested_qp, **after_before_qp,
                                 **limit_offset_qp, **order_by_qp)
    if extended:
        harvests = [{
            "id": harvest.id,
            'season_id': harvest.season_id,
            'owner_id': harvest.owner_id,
            "date": harvest.date,
            "fruit": harvest.fruit,
            "harvested": harvest.harvested,
            "harvested_by_employees": harvest.harvested_by_employees,
            "self_harvested": harvest.self_harvested,
            "price": harvest.price,
            "avg_pay_per_kg": harvest.avg_pay_per_kg,
            "total_profits": harvest.total_profits,
            "harvested_by_emp_profits": harvest.harvested_by_employees * harvest.price,
            "self_harvested_profits": harvest.self_harvested_profits,
            "total_paid": harvest.harvested_by_employees * harvest.avg_pay_per_kg,
            "net_profit": harvest.net_profit,
            "best_employee": harvest.best_employee if harvest.best_employee else {},
        } for harvest in harvests]
    else:
        harvests = [dict((col, getattr(h, col)) for col in h.__table__.columns.keys()) for h in harvests]
    if data_format == 'csv':
        filename = f"season_{year}_harvests" if not extended else f"season_{year}_harvests_ext"
        compressed_file, tmp_dir = create_temp_csv(data=harvests,
                                                   filename=filename,
                                                   column_names=[k for k in harvests[0].keys()])
        background_tasks.add_task(delete_temp_files, tmp_dir)
        return FileResponse(path=os.path.join(tmp_dir, compressed_file), filename=compressed_file,
                            media_type='application/zip')
    return harvests


@router.post("/{year}/employees", status_code=status.HTTP_201_CREATED,
             response_model=sc.EmployeeResponseHarvests)
def employees_post(year: int,
                   employee_data: sc.EmployeeCreate,
                   user: m.User = Depends(get_current_active_user),
                   db: Session = Depends(get_db)):
    return crud.employee_create(db=db, user=user, year=year, data=employee_data)


@router.get("/{year}/employees", status_code=status.HTTP_200_OK,
            response_model=Union[List[sc.EmployeeResponseExtended], List[sc.EmployeeResponse]])
def employees_get(background_tasks: BackgroundTasks,
                  year: int,
                  user: m.User = Depends(get_current_active_user),
                  db: Session = Depends(get_db),
                  after_before_qp=Depends(after_before),
                  limit_offset_qp=Depends(limit_offset),
                  order_by_qp=Depends(order_by_query),
                  name: Optional[str] = Query(None, min_length=2, max_length=10, regex=r"[a-zA-Z]+"),
                  data_format: Optional[str] = Query('json', min_length=3, max_length=4),
                  extended: Optional[bool] = Query(False)):
    if data_format not in ('json', 'csv'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Data format must be 'json' or 'csv', not '{data_format}'")
    employees = crud.employees_get(db=db, user=user, year=year, name=name,
                                   **after_before_qp, **limit_offset_qp, **order_by_qp)
    if extended:
        employees = [{
            "id": employee.id,
            "name": employee.name,
            "start_date": employee.start_date,
            "end_date": employee.end_date,
            'season_id': employee.season_id,
            'employer_id': employee.employer_id,
            'total_harvested': employee.total_harvested,
            "total_earnings": employee.total_earnings,
            "harvested_per_fruit": employee.harvested_per_fruit if employee.harvested_per_fruit else {},
            "earnings_per_fruit": employee.earned_per_fruit if employee.earned_per_fruit else {},
            'best_harvest': employee.best_harvest['date'],
        } for employee in employees]
    else:
        employees = [dict((col, getattr(e, col)) for col in e.__table__.columns.keys()) for e in employees]
    if data_format == 'csv':
        filename = f"season_{year}_employees" if not extended else f"season_{year}_employees_ext"
        compressed_file, tmp_dir = create_temp_csv(data=employees,
                                                   filename=filename,
                                                   column_names=[k for k in employees[0].keys()])
        background_tasks.add_task(delete_temp_files, tmp_dir)
        return FileResponse(path=os.path.join(tmp_dir, compressed_file), filename=compressed_file,
                            media_type='application/zip')
    return employees


@router.post("/{year}/expenses", status_code=status.HTTP_201_CREATED,
             response_model=sc.ExpenseResponse)
def expenses_post(year: int,
                  expense_data: sc.ExpenseCreate,
                  user: m.User = Depends(get_current_active_user),
                  db: Session = Depends(get_db)):
    return crud.expense_create(db=db, year=year, user=user, data=expense_data)


@router.get("/{year}/expenses", status_code=status.HTTP_200_OK,
            response_model=List[sc.ExpenseResponse])
def expenses_get(background_tasks: BackgroundTasks,
                 year: int,
                 user: m.User = Depends(get_current_active_user),
                 db: Session = Depends(get_db),
                 type: Optional[str] = Query(None, min_length=2, max_length=30, regex=r"[a-zA-Z]+"),
                 more: Optional[decimal.Decimal] = Query(None, gt=0),
                 less: Optional[decimal.Decimal] = Query(None, gt=0),
                 after_before_qp=Depends(after_before),
                 limit_offset_qp=Depends(limit_offset),
                 order_by_qp=Depends(order_by_query),
                 data_format: Optional[str] = Query('json', min_length=3, max_length=4)):
    if data_format not in ('json', 'csv'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Data format must be 'json' or 'csv', not '{data_format}'")
    expenses = crud.expenses_get(db=db, user=user, year=year, type=type, more=more, less=less,
                                 **after_before_qp, **limit_offset_qp,  **order_by_qp)
    if data_format == 'csv':
        expenses_dicts = [dict((col, getattr(e, col)) for col in e.__table__.columns.keys()) for e in expenses]
        filename = f"season_{year}_expenses"
        compressed_file, tmp_dir = create_temp_csv(data=expenses_dicts,
                                                   filename=filename,
                                                   column_names=[k for k in expenses_dicts[0].keys()])
        background_tasks.add_task(delete_temp_files, tmp_dir)
        return FileResponse(path=os.path.join(tmp_dir, compressed_file), filename=compressed_file,
                            media_type='application/zip')
    return expenses


@router.get("/{year}/summary")
def report_single_season(year: int,
                         user: m.User = Depends(get_current_active_user),
                         db: Session = Depends(get_db)):
    season = crud.season_get(db=db, user=user, year=year)[0]
    season_report = {
        'id': season.id,
        'year': year,
        'start_date': season.start_date,
        'end_date': season.end_date,
        'fruits': season.fruits,
        'employees_n': len(season.employees),
        'best_employee': season.best_employee,
        'best_employee_per_fruit': season.best_employees_per_fruit,
        'harvests_n': len(season.harvests),
        'best_harvest': season.best_harvest,
        'total_harvested_value': season.total_harvested_value,
        'total_employee_payments': season.total_employee_payments,
        'harvested_per_fruit': season.harvested_per_fruit,
        'value_per_fruit': season.value_per_fruit,
        'total_expenses_value': season.total_expenses_value,
        'net_profits': season.total_harvested_value - season.total_employee_payments - season.total_expenses_value
    }
    return season_report
