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
def post_season(season_data: sc.SeasonBase,
                user: mod.User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    season_m_new = crud.season_create(db, user, season_data.start_date)
    return season_m_new


@router.get("/", status_code=status.HTTP_200_OK, response_model=sc.SeasonListResponse,
            response_model_exclude_none=True)
def get_all_seasons(user: mod.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    seasons_m = crud.season_get_all(db, user)
    return seasons_m


@router.get("/")
def get_season_by_year():
    pass
