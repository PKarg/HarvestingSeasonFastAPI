from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
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
                     db: Session = Depends(get_db),
                     after: Optional[str] = Query(None),
                     before: Optional[str] = Query(None),
                     fruit: Optional[str] = Query(None, min_length=5, max_length=20),
                     p_more: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                     p_less: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                     h_more: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                     h_less: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$")
                     ):
    harvests_m_all: List[m.Harvest] = crud.harvest_get(db, user, after=after, before=before, fruit=fruit,
                                                       p_more=p_more, p_less=p_less, h_more=h_more, h_less=h_less)
    return harvests_m_all


@router.get("/{id}", status_code=status.HTTP_200_OK,
            response_model=sc.HarvestResponse)
def harvests_get_all(id: int,
                     user: m.User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    try:
        harvests_m: m.Harvest = crud.harvest_get(db, user, id=id)[0]
        return harvests_m
    except IndexError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object with given id doesn't exist")
