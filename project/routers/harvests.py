from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from project.auth import get_current_user
from project.data import models as m, schemas as sc
from project.dependencies import get_db
from . import crud

router = APIRouter(
    prefix="/harvests",
    tags=["harvests"]
)


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[sc.HarvestResponseALL])
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
    return crud.harvests_get(db, user, after=after, before=before, fruit=fruit, year=year, season_id=season_id, p_more=p_more, p_less=p_less, h_more=h_more, h_less=h_less)


@router.get("/{h_id}", status_code=status.HTTP_200_OK,
            response_model=sc.HarvestResponseALL)
def harvests_get_id(h_id: int,
                    user: m.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    try:
        return crud.harvests_get(db, user, id=h_id)[0]
    except IndexError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object with given id doesn't exist")


@router.delete("/{h_id}", status_code=status.HTTP_200_OK,
               response_model=None)
def harvests_delete(h_id: int,
                    user: m.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    harvest_m = crud.harvests_get(db, user, id=h_id)[0]
    db.delete(harvest_m)
    db.commit()


@router.patch("/{h_id}", status_code=status.HTTP_200_OK,
              response_model=sc.HarvestResponse)
def harvests_update(h_id: int,
                    harvest_data: sc.HarvestUpdate,
                    user: m.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    harvest_m_updated = crud.harvest_update(db=db, user=user, id=h_id, data=harvest_data)
    return harvest_m_updated


@router.get("/{h_id}/employees", status_code=status.HTTP_200_OK,
            response_model=List[sc.EmployeeResponse])
def harvests_get_employees(h_id: int,
                           user: m.User = Depends(get_current_user),
                           db: Session = Depends(get_db),
                           after: Optional[str] = Query(None, min_length=10, max_length=10,regex=r"^[0-9]+(-[0-9]+)+$"),
                           before: Optional[str] = Query(None, min_length=10, max_length=10,regex=r"^[0-9]+(-[0-9]+)+$"),
                           name: Optional[str] = Query(None, min_length=2, max_length=10, regex=r"[a-zA-Z]+")):
    return crud.employees_get(db=db, user=user, harvest_id=h_id, after=after, before=before, name=name)


@router.get("/{id}/workdays", status_code=status.HTTP_200_OK,
            response_model=List[sc.WorkdayResponse])
def harvests_get_workdays(h_id: int,
                          user: m.User = Depends(get_current_user),
                          db: Session = Depends(get_db),
                          p_more: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                          p_less: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                          h_more: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                          h_less: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                          fruit: Optional[str] = Query(None, min_length=5, max_length=20)):
    return crud.workdays_get(db=db, user=user, h_id=h_id, p_more=p_more,
                             p_less=p_less, h_more=h_more, h_less=h_less,
                             fruit=fruit)


@router.post("/{id}/workdays", status_code=status.HTTP_201_CREATED,
             response_model=sc.WorkdayResponse)
def harvests_post_workday(h_id: int,
                          workday_data: sc.WorkdayCreate,
                          user: m.User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    return crud.workday_create(db=db, user=user, data=workday_data, h_id=h_id)
