from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user
from data import models as m, schemas as sc
from dependencies import get_db
from . import crud

router = APIRouter(
    prefix="/workdays",
    tags=["workdays"]
)


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[sc.WorkdayResponse])
def workdays_get_all(user: m.User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    # TODO implement
    pass


@router.get("/{w_id}", status_code=status.HTTP_200_OK,
            response_model=sc.WorkdayResponse)
def workday_get_id(w_id: int,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    # TODO implement
    pass


@router.patch("/{w_id}", status_code=status.HTTP_200_OK,
              response_model=sc.WorkdayResponse)
def workday_update(w_id: int,
                   workday_data: sc.WorkdayUpdate,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    # TODO implement
    pass


@router.put("/{w_id}", status_code=status.HTTP_200_OK,
            response_model=sc.WorkdayResponse)
def workday_replace(w_id: int,
                    workday_data: sc.WorkdayCreate,
                    user: m.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    # TODO implement
    pass


@router.delete("/{w_id}", status_code=status.HTTP_200_OK)
def workday_update(w_id: int,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    # TODO implement
    pass