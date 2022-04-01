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
def add_season(season_data: sc.SeasonBase,
               user: mod.User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    new_season = crud.create_season(db, user, season_data.start_date)
    return new_season
