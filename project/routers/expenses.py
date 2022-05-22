from typing import List, Optional

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from project.auth import get_current_user
from project.data import models as m, schemas as sc
from project.dependencies import get_db
from . import crud

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"]
)


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[sc.ExpenseResponse])
def expense_get_all(user: m.User = Depends(get_current_user),
                    db: Session = Depends(get_db),
                    type: Optional[str] = Query(None, min_length=2, max_length=30, regex=r"[a-zA-Z]+"),
                    after: Optional[str] = Query(None, min_length=10, max_length=10, regex=r"^[0-9]+(-[0-9]+)+$"),
                    before: Optional[str] = Query(None, min_length=10, max_length=10, regex=r"^[0-9]+(-[0-9]+)+$"),
                    more: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                    less: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                    season_id: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$")):
    return crud.expenses_get(db=db, user=user, season_id=season_id, type=type, after=after,
                             before=before, more=more, less=less)


@router.get("/{ex_id}", status_code=status.HTTP_200_OK,
            response_model=sc.ExpenseResponse)
def expense_get_id(ex_id: int,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    return crud.expenses_get(db=db, user=user, id=ex_id)[0]


@router.patch("/{ex_id}", status_code=status.HTTP_200_OK,
              response_model=sc.ExpenseResponse)
def expense_update(ex_id: int,
                   expense_data: sc.ExpenseUpdate,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    return crud.expense_update(db=db, id=ex_id, user=user, data=expense_data)


@router.put("/{ex_id}", status_code=status.HTTP_200_OK,
            response_model=sc.ExpenseResponse)
def expense_replace(ex_id: int,
                    expense_data: sc.ExpenseReplace,
                    user: m.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    # TODO implement
    pass


@router.delete("/{e_id}", status_code=status.HTTP_200_OK)
def expense_update(ex_id: int,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    expense_to_delete = crud.expenses_get(db=db, user=user, id=ex_id)[0]
    db.delete(expense_to_delete)
    db.commit()
