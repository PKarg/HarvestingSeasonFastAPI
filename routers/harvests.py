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
                     year: Optional[str] = Query(None, min_length=4, max_length=4, regex=r"^ *\d[\d ]*$"),
                     season_id: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                     after: Optional[str] = Query(None),
                     before: Optional[str] = Query(None),
                     fruit: Optional[str] = Query(None, min_length=5, max_length=20),
                     p_more: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                     p_less: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                     h_more: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                     h_less: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$")
                     ):
    harvests_m_all: List[m.Harvest] = crud.harvest_get(db, user, after=after, before=before, fruit=fruit, year=year,
                                                       season_id=season_id, p_more=p_more, p_less=p_less, h_more=h_more, h_less=h_less)
    return harvests_m_all


@router.get("/{h_id}", status_code=status.HTTP_200_OK,
            response_model=sc.HarvestResponse)
def harvests_get_id(h_id: int,
                    user: m.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    try:
        harvests_m: m.Harvest = crud.harvest_get(db, user, id=h_id)[0]
        return harvests_m
    except IndexError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object with given id doesn't exist")


@router.delete("/{h_id}", status_code=status.HTTP_200_OK,
               response_model=None)
def harvests_delete(h_id: int,
                    user: m.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    harvest_m = crud.harvest_get(db, user, id=h_id)[0]
    db.delete(harvest_m)
    db.commit()


@router.put("/{h_id}", status_code=status.HTTP_200_OK,
            response_model=sc.HarvestResponse)
def harvests_change(h_id: int,
                    harvest_data: sc.HarvestReplace,
                    user: m.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    # TODO implement
    pass


@router.patch("/{h_id}", status_code=status.HTTP_200_OK,
              response_model=sc.HarvestResponse)
def harvests_update(h_id: int,
                    harvest_data: sc.HarvestUpdate,
                    user: m.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    # TODO implement
    pass


@router.get("/{h_id}/employees", status_code=status.HTTP_200_OK,
            response_model=List[sc.EmployeeResponse])
def harvests_get_employees(h_id: int,
                           user: m.User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    # TODO implement
    pass


@router.get("/{id}/workdays", status_code=status.HTTP_200_OK,
            response_model=List[sc.WorkdayResponse])
def harvests_get_employees(h_id: int,
                           user: m.User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    # TODO implement
    pass


@router.post("/{id}/workdays", status_code=status.HTTP_201_CREATED,
             response_model=sc.WorkdayResponse)
def harvests_get_employees():
    # TODO implement
    pass
