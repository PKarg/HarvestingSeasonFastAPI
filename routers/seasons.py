from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user
from data import models as mod, schemas as sc
from dependencies import get_db
from . import crud

router = APIRouter(
    prefix="/seasons",
    tags=["seasons"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def seasons_post(season_data: sc.SeasonBase,
                 user: mod.User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    season_m_new = crud.season_create(db, user, season_data.start_date)
    return season_m_new


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[sc.SeasonResponse])
def seasons_get_all(user: mod.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    seasons_m_all = crud.season_get_all(db, user)
    return seasons_m_all


@router.get("/{year}", status_code=status.HTTP_200_OK,
            response_model=sc.SeasonResponse)
def seasons_get_by_year(year: int,
                        user: mod.User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    season_m = crud.season_get_by_year(db, user, year)
    return season_m


@router.patch("/{year", status_code=status.HTTP_200_OK,
              response_model=sc.SeasonResponse)
def seasons_update(year: int, season_data: sc.SeasonUpdate,
                   user: mod.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    season_m = crud.season_get_by_year(db, user, year)
    season_m_updated = crud.season_update(db, season_m, season_data.start_date, season_data.end_date)
    return season_m_updated


@router.post("/{year}/harvests", status_code=status.HTTP_201_CREATED,
             response_model=sc.HarvestResponseEmployees)
def harvests_post(year: int,
                  harvest_data: sc.HarvestCreate,
                  user: mod.User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    season_m = crud.season_get_by_year(db, user, year)
    harvest_m_new = crud.harvest_create(db, user, season_m, harvest_data)
    return harvest_m_new


@router.get("{year}/harvests", status_code=status.HTTP_200_OK,
            response_model=List[sc.HarvestResponse])
def harvests_get(year: int,
                 user: mod.User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    season_m = crud.season_get_by_year(db, user, year)
    return season_m.harvests


@router.post("/{year}/employees", status_code=status.HTTP_201_CREATED,
             response_model=sc.EmployeeResponseHarvests)
def employees_post(year: int,
                   employee_data: sc.EmployeeCreate,
                   user: mod.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    season_m = crud.season_get_by_year(db, user, year)
    harvest_m_new = crud.employee_create(db, user, season_m, employee_data)
    return harvest_m_new


@router.get("{year}/employees", status_code=status.HTTP_200_OK,
            response_model=List[sc.EmployeeResponse])
def harvests_get(year: int,
                 user: mod.User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    season_m = crud.season_get_by_year(db, user, year)
    return season_m.employees
