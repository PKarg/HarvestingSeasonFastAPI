from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from data import models, schemas
from dependencies import get_db
from . import crud

router = APIRouter(
    prefix="/seasons",
    tags=["seasons"],
)


@router.post("/")
def add_season(season_data: schemas.SeasonBase,
               user: models.User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    new_season = crud.create_season(db, user, season_data.start_date)
    return new_season
