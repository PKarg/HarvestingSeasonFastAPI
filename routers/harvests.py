from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user
from data import models as m, schemas as sc
from dependencies import get_db
from . import crud

router = APIRouter(
    prefix="/harvests",
    tags=["harvests"]
)


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[sc.SeasonResponse])
def harvests_get_all(user: m.User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    harvests_m_all = crud.harvests_m_all(db, user)
    return harvests_m_all
