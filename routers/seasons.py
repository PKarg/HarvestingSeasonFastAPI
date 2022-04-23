from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user
from data import models as m, schemas as sc
from dependencies import get_db
from . import crud

router = APIRouter(
    prefix="/seasons",
    tags=["seasons"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def seasons_post(season_data: sc.SeasonBase,
                 user: m.User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    season_m_new = crud.season_create(db, user, season_data.start_date)
    return season_m_new


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[sc.SeasonResponse])
def seasons_get_all(user: m.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    seasons_m_all = crud.season_get_all(db, user)
    return seasons_m_all


@router.get("/{year}", status_code=status.HTTP_200_OK,
            response_model=sc.SeasonResponse)
def seasons_get_by_year(year: int,
                        user: m.User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    season_m = crud.season_get_by_year(db, user, year)
    return season_m


@router.patch("/{year}", status_code=status.HTTP_200_OK,
              response_model=sc.SeasonResponse)
def seasons_update(year: int, season_data: sc.SeasonUpdate,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    season_m = crud.season_get_by_year(db, user, year)
    season_m_updated = crud.season_update(db, season_m, season_data.start_date, season_data.end_date)
    return season_m_updated


@router.delete("/{year}", status_code=status.HTTP_200_OK)
def seasons_update(year: int,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    season_m = crud.season_get_by_year(db, user, year)
    db.delete(season_m)
    db.commit()


@router.post("/{year}/harvests", status_code=status.HTTP_201_CREATED,
             response_model=sc.HarvestResponseEmployees)
def harvests_post(year: int,
                  harvest_data: sc.HarvestCreate,
                  user: m.User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    season_m = crud.season_get_by_year(db, user, year)

    if season_m.start_date <= harvest_data.date:
        if season_m.end_date:
            if season_m.end_date >= harvest_data.date:
                harvest_m_new = crud.harvest_create(db, user, season_m.id, harvest_data)
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Harvest date can't be after the season end date")
        else:
            harvest_m_new = crud.harvest_create(db, user, season_m, harvest_data)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Harvest date can't be before the season start date")
    return harvest_m_new


@router.get("{year}/harvests", status_code=status.HTTP_200_OK,
            response_model=List[sc.HarvestResponse])
def harvests_get(year: int,
                 user: m.User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    season_m = crud.season_get_by_year(db, user, year)
    return season_m.harvests


@router.post("/{year}/employees", status_code=status.HTTP_201_CREATED,
             response_model=sc.EmployeeResponseHarvests)
def employees_post(year: int,
                   employee_data: sc.EmployeeCreate,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    season_m = crud.season_get_by_year(db, user, year)
    harvest_m_new = crud.employee_create(db, user, season_m, employee_data)
    return harvest_m_new


@router.get("{year}/employees", status_code=status.HTTP_200_OK,
            response_model=List[sc.EmployeeResponse])
def harvests_get(year: int,
                 user: m.User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    season_m = crud.season_get_by_year(db, user, year)
    return season_m.employees


@router.post("/{year}/expenses", status_code=status.HTTP_201_CREATED,
             response_model=sc.ExpenseResponse)
def expenses_get(year: int,
                 expense_data: sc.ExpenseCreate,
                 user: m.User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    season_m: m.Season = crud.season_get_by_year(db, user, year)
    expense_m_new: m.Expense = crud.expense_create(db, season_m, expense_data)
    return expense_m_new


@router.get("/{year}/expenses", status_code=status.HTTP_200_OK,
            response_model=sc.ExpenseResponse)
def expenses_get(year: int,
                 user: m.User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    season_m: m.Season = crud.season_get_by_year(db, user, year)
    return season_m.expenses
