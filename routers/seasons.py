from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user
from data import models as mod, schemas as sc
from dependencies import get_db
from . import crud

router = APIRouter(
    prefix="/seasons",
    tags=["seasons"],
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=sc.SeasonResponse,
             response_model_exclude_none=True)
def seasons_post(season_data: sc.SeasonBase,
                user: mod.User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    season_m_new = crud.season_create(db, user, season_data.start_date)
    return season_m_new


@router.get("/", status_code=status.HTTP_200_OK,
            response_model_exclude_none=True)
def seasons_get_all(user: mod.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    seasons_m_all = crud.season_get_all(db, user)
    return seasons_m_all


# TODO add status code
# TODO add response model
@router.get("/{year}")
def seasons_get_by_year(year: int,
                       user: mod.User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    season_m = crud.season_get_by_year(db, user, year)
    return season_m


# TODO add status code
# TODO add response model
@router.post("/{year}/harvests")
def harvests_post(year: int,
                  harvest_data: sc.HarvestCreate,
                  user: mod.User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    season_m = crud.season_get_by_year(db, user, year)
    harvest_m_new = crud.harvest_create(db, user, season_m, harvest_data)
    return harvest_m_new


# TODO add status code
# TODO add response model
@router.post("/{year}/employees")
def harvests_post(year: int,
                  employee_data: sc.EmployeeCreate,
                  user: mod.User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    season_m = crud.season_get_by_year(db, user, year)
    harvest_m_new = crud.employee_create(db, user, season_m, employee_data)
    return harvest_m_new
