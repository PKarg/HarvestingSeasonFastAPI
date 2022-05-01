from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user
from data import models as m, schemas as sc
from dependencies import get_db
from . import crud

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"]
)


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[sc.ExpenseResponse])
def expense_get_all(user: m.User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    # TODO implement
    pass


@router.get("/{e_id}", status_code=status.HTTP_200_OK,
            response_model=sc.ExpenseResponse)
def expense_get_id(e_id: int,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    # TODO implement
    pass


@router.patch("/{e_id}", status_code=status.HTTP_200_OK,
              response_model=sc.ExpenseResponse)
def expense_update(e_id: int,
                   expense_data: sc.ExpenseUpdate,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    # TODO implement
    pass


@router.put("/{e_id}", status_code=status.HTTP_200_OK,
            response_model=sc.ExpenseResponse)
def expense_replace(e_id: int,
                    expense_data: sc.ExpenseReplace,
                    user: m.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    # TODO implement
    pass


@router.delete("/{e_id}", status_code=status.HTTP_200_OK)
def expense_update(e_id: int,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    # TODO implement
    pass
