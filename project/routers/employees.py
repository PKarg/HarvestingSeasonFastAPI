import os
from typing import List, Optional

from fastapi import APIRouter, Depends, status, Query, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from project.auth import get_current_active_user
from project.data import models as m, schemas as sc
from project.dependencies import get_db, after_before, price_harvested_more_less, limit_offset, order_by_query
from . import crud
from ..additional import create_temp_csv, delete_temp_files

router = APIRouter(
    prefix="/emlpoyees",
    tags=["employees"]
)


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[sc.EmployeeResponseALL])
def employees_get_all(user: m.User = Depends(get_current_active_user),
                      db: Session = Depends(get_db),
                      season_id: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                      after_before_qp=Depends(after_before),
                      limit_offset_qp=Depends(limit_offset),
                      order_by_qp=Depends(order_by_query),
                      name: Optional[str] = Query(None, min_length=2, max_length=10, regex=r"[a-zA-Z]+")):
    return crud.employees_get(db=db, user=user, **after_before_qp,
                              name=name, season_id=season_id, **limit_offset_qp, **order_by_qp)


@router.get("/{e_id}", status_code=status.HTTP_200_OK,
            response_model=sc.EmployeeResponseALL)
def employees_get_id(e_id: int,
                     user: m.User = Depends(get_current_active_user),
                     db: Session = Depends(get_db)):
    return crud.employees_get(db=db, user=user, id=e_id)[0]


@router.patch("/{e_id}", status_code=status.HTTP_200_OK,
              response_model=sc.EmployeeResponse)
def employees_update(e_id: int,
                     employee_data: sc.EmployeeUpdate,
                     user: m.User = Depends(get_current_active_user),
                     db: Session = Depends(get_db)):
    return crud.employee_update(db=db, user=user, id=e_id, data=employee_data)


@router.delete("/{e_id}", status_code=status.HTTP_200_OK)
def employee_delete(e_id: int,
                    user: m.User = Depends(get_current_active_user),
                    db: Session = Depends(get_db)):
    employee_to_delete: m.Employee = crud.employees_get(id=e_id, user=user, db=db)[0]
    db.delete(employee_to_delete)
    db.commit()


@router.get("/{e_id}/harvests", status_code=status.HTTP_200_OK,
            response_model=List[sc.HarvestResponse])
def employee_get_harvests(e_id: int,
                          user: m.User = Depends(get_current_active_user),
                          db: Session = Depends(get_db),
                          after_before_qp=Depends(after_before),
                          fruit: Optional[str] = Query(None, min_length=5, max_length=20),
                          price_harvested_qp=Depends(price_harvested_more_less),
                          limit_offset_qp=Depends(limit_offset),
                          order_by_qp=Depends(order_by_query)):
    return crud.harvests_get(db=db, user=user, employee_id=e_id,
                             **after_before_qp, fruit=fruit,
                             **price_harvested_qp, **limit_offset_qp, **order_by_qp)


@router.get("/{e_id}/workdays", status_code=status.HTTP_200_OK,
            response_model=List[sc.WorkdayResponse])
def employee_get_workdays(e_id: int,
                          user: m.User = Depends(get_current_active_user),
                          db: Session = Depends(get_db),
                          price_harvested_qp=Depends(price_harvested_more_less),
                          fruit: Optional[str] = Query(None, min_length=5, max_length=20),
                          limit_offset_qp=Depends(limit_offset),
                          order_by_qp=Depends(order_by_query)):
    return crud.workdays_get(db=db, user=user, e_id=e_id, **price_harvested_qp,
                             fruit=fruit, **limit_offset_qp, **order_by_qp)


@router.post("/{e_id}/workdays", status_code=status.HTTP_201_CREATED,
             response_model=sc.WorkdayResponse)
def employee_create_workday(e_id: int,
                            workday_data: sc.WorkdayCreate,
                            user: m.User = Depends(get_current_active_user),
                            db: Session = Depends(get_db)):
    return crud.workday_create(db=db, user=user, data=workday_data, e_id=e_id)


@router.get("/{e_id}/summary", status_code=status.HTTP_200_OK)
def get_employee_summary(e_id: int,
                         user: m.User = Depends(get_current_active_user),
                         db: Session = Depends(get_db)):
    employee = crud.employees_get(db=db, user=user, id=e_id)[0]
    summary = {
        "id": employee.id,
        'season_id': employee.season_id,
        'employer_id': employee.employer_id,
        "name": employee.name,
        "start_date": employee.start_date,
        "end_date": employee.end_date,
        'total_harvested': employee.total_harvested,
        "total_earnings": employee.total_earnings,
        "harvested_per_fruit": employee.harvested_per_fruit,
        "earnings_per_fruit": employee.earned_per_fruit,
        'best_harvest': employee.best_harvest,
        "harvest_history": employee.harvests_history
    }
    return summary


@router.get("/{e_id}/harvests-summary", status_code=status.HTTP_200_OK)
def harvests_get_harvest_employees_summary(background_tasks: BackgroundTasks,
                                           e_id: int,
                                           user: m.User = Depends(get_current_active_user),
                                           db: Session = Depends(get_db),
                                           data_format: str = Query('json', min_length=3, max_length=4)):
    if data_format not in ('json', 'csv'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Data format must be 'json' or 'csv', not '{data_format}'")
    employee = crud.employees_get(db=db, user=user, id=e_id)[0]
    if not employee.harvests_history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Employee with id {e_id} has no registered harvests")
    if data_format == 'csv':
        filename = f"employee_{employee.name}_{employee.id}_harvests"
        compressed_file, tmp_dir = create_temp_csv(data=employee.harvests_history,
                                                   filename=filename,
                                                   column_names=[k for k in employee.harvests_history[0].keys()])
        background_tasks.add_task(delete_temp_files, tmp_dir)
        return FileResponse(path=os.path.join(tmp_dir, compressed_file), filename=compressed_file,
                            media_type='application/zip')
    else:
        return employee.harvests_history
