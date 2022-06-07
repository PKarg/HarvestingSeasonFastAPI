import decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from project.auth import get_current_active_user
from project.data import models as m, schemas as sc
from project.dependencies import get_db, limit_offset, after_before, price_harvested_more_less
from . import crud

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
                    after_before_qp=Depends(after_before)):
    return crud.season_get(db=db, user=user, **after_before_qp,
                           **limit_offset_qp)


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
            response_model=List[sc.HarvestResponse])
def harvests_get(year: int,
                 user: m.User = Depends(get_current_active_user),
                 db: Session = Depends(get_db),
                 after_before_qp=Depends(after_before),
                 fruit: Optional[str] = Query(None, min_length=3, max_length=30),
                 price_harvested_qp=Depends(price_harvested_more_less),
                 limit_offset_qp=Depends(limit_offset)):
    return crud.harvests_get(db, user, year=year,
                             fruit=fruit, **price_harvested_qp, **after_before_qp, **limit_offset_qp)


@router.post("/{year}/employees", status_code=status.HTTP_201_CREATED,
             response_model=sc.EmployeeResponseHarvests)
def employees_post(year: int,
                   employee_data: sc.EmployeeCreate,
                   user: m.User = Depends(get_current_active_user),
                   db: Session = Depends(get_db)):
    return crud.employee_create(db=db, user=user, year=year, data=employee_data)


@router.get("/{year}/employees", status_code=status.HTTP_200_OK,
            response_model=List[sc.EmployeeResponse])
def employees_get(year: int,
                  user: m.User = Depends(get_current_active_user),
                  db: Session = Depends(get_db),
                  after_before_qp=Depends(after_before),
                  limit_offset_qp=Depends(limit_offset),
                  name: Optional[str] = Query(None, min_length=2, max_length=10, regex=r"[a-zA-Z]+")):
    return crud.employees_get(db=db, user=user, year=year, name=name, **after_before_qp, **limit_offset_qp)


@router.post("/{year}/expenses", status_code=status.HTTP_201_CREATED,
             response_model=sc.ExpenseResponse)
def expenses_post(year: int,
                  expense_data: sc.ExpenseCreate,
                  user: m.User = Depends(get_current_active_user),
                  db: Session = Depends(get_db)):
    return crud.expense_create(db=db, year=year, user=user, data=expense_data)


@router.get("/{year}/expenses", status_code=status.HTTP_200_OK,
            response_model=List[sc.ExpenseResponse])
def expenses_get(year: int,
                 user: m.User = Depends(get_current_active_user),
                 db: Session = Depends(get_db),
                 type: Optional[str] = Query(None, min_length=2, max_length=30, regex=r"[a-zA-Z]+"),
                 more: Optional[decimal.Decimal] = Query(None, gt=0),
                 less: Optional[decimal.Decimal] = Query(None, gt=0),
                 after_before_qp=Depends(after_before),
                 limit_offset_qp=Depends(limit_offset)):
    return crud.expenses_get(db=db, user=user, year=year, type=type, more=more, less=less,
                             **after_before_qp, **limit_offset_qp)
