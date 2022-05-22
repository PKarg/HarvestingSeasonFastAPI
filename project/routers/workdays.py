from typing import List, Optional

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from project.auth import get_current_user
from project.data import models as m, schemas as sc
from project.dependencies import get_db
from . import crud

router = APIRouter(
    prefix="/workdays",
    tags=["workdays"]
)


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[sc.WorkdayResponse])
def workdays_get_all(user: m.User = Depends(get_current_user),
                     db: Session = Depends(get_db),
                     p_more: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                     p_less: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                     h_more: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                     h_less: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                     fruit: Optional[str] = Query(None, min_length=5, max_length=20)
                     ):
    return crud.workdays_get(db=db, user=user, p_more=p_more, p_less=p_less,
                             h_more=h_more, h_less=h_less, fruit=fruit)


@router.get("/{w_id}", status_code=status.HTTP_200_OK,
            response_model=sc.WorkdayResponse)
def workday_get_id(w_id: int,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    return crud.workdays_get(db=db, user=user, id=w_id)[0]


@router.patch("/{w_id}", status_code=status.HTTP_200_OK,
              response_model=sc.WorkdayResponse)
def workday_update(w_id: int,
                   workday_data: sc.WorkdayUpdate,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    return crud.workday_update(db=db, user=user, id=w_id, data=workday_data)


@router.delete("/{w_id}", status_code=status.HTTP_200_OK)
def workday_update(w_id: int,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    workday_to_delete: m.Workday = crud.workdays_get(db=db, user=user, id=w_id)[0]
    db.delete(workday_to_delete)
    db.commit()
