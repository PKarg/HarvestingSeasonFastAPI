from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from auth import get_current_user
from data import models as m, schemas as sc
from dependencies import get_db
from . import crud

router = APIRouter(
    prefix="/emlpoyees",
    tags=["employees"]
)


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[sc.EmployeeResponse])
def employees_get_all(user: m.User = Depends(get_current_user),
                      db: Session = Depends(get_db),
                      season_id: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                      after: Optional[str] = Query(None, min_length=10, max_length=10, regex=r"^[0-9]+(-[0-9]+)+$"),
                      before: Optional[str] = Query(None, min_length=10, max_length=10, regex=r"^[0-9]+(-[0-9]+)+$"),
                      name: Optional[str] = Query(None, min_length=2, max_length=10, regex=r"[a-zA-Z]+")):
    return crud.employee_get(db=db, user=user, after=after, before=before, name=name, season_id=season_id)


@router.get("/{e_id}", status_code=status.HTTP_200_OK,
            response_model=sc.EmployeeResponse)
def employees_get_id(e_id: int,
                     user: m.User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    return crud.employee_get(db=db, user=user, id=e_id)[0]


@router.patch("/{e_id}", status_code=status.HTTP_200_OK,
              response_model=sc.EmployeeResponse)
def employees_update(e_id: int,
                     user: m.User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    # TODO - implement
    pass


@router.put("/{e_id}", status_code=status.HTTP_200_OK,
            response_model=sc.EmployeeResponse)
def employees_replace(e_id: int,
                      employee_data: sc.EmployeeReplace,
                      user: m.User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    # TODO - implement
    pass


@router.delete("/{e_id}", status_code=status.HTTP_200_OK)
def employee_delete(e_id: int,
                    user: m.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    # TODO - implement
    pass


@router.get("/{e_id}/harvests", status_code=status.HTTP_200_OK,
            response_model=List[sc.HarvestResponse])
def employee_get_harvests(e_id: int,
                          user: m.User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    # TODO add lacking filters
    return crud.harvest_get(db=db, user=user, employee_id=e_id)


@router.get("/{e_id}/workdays", status_code=status.HTTP_200_OK,
            response_model=List[sc.WorkdayResponse])
def employee_get_workdays(e_id: int,
                          user: m.User = Depends(get_current_user),
                          db: Session = Depends(get_db),
                          p_more: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                          p_less: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                          h_more: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                          h_less: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                          fruit: Optional[str] = Query(None, min_length=5, max_length=20)):
    return crud.workdays_get(db=db, user=user, e_id=e_id, p_more=p_more,
                             p_less=p_less, h_more=h_more, h_less=h_less,
                             fruit=fruit)


@router.post("/{e_id}/workdays", status_code=status.HTTP_201_CREATED,
             response_model=sc.WorkdayResponse)
def employee_create_workday(e_id: int,
                            workday_data: sc.WorkdayCreate,
                            user: m.User = Depends(get_current_user),
                            db: Session = Depends(get_db)):
    return crud.workday_create(db=db, user=user, data=workday_data, e_id=e_id)

