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
            response_model=List[sc.HarvestResponse])
def harvests_get_all(user: m.User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    harvests_m_all: List[m.Harvest] = crud.harvest_get(db, user)
    return harvests_m_all


@router.get("/{id}", status_code=status.HTTP_200_OK,
            response_model=sc.HarvestResponse)
def harvests_get_all(id: int,
                     user: m.User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    try:
        harvests_m: m.Harvest = crud.harvest_get(db, user, id=id)[0]
        return harvests_m
    except IndexError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object with given id doesn't exist")
