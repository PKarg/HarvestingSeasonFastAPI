from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
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
            response_model=sc.EmployeeResponse)
def employees_get_all(user: m.User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    # TODO - implement
    pass


@router.get("/{e_id}", status_code=status.HTTP_200_OK,
            response_model=sc.EmployeeResponse)
def employees_get_id(e_id: int,
                     user: m.User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    # TODO - implement
    pass


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
    # TODO - implement
    pass


@router.get("/{e_id}/workdays", status_code=status.HTTP_200_OK,
            response_model=List[sc.WorkdayResponse])
def employee_get_workdays(e_id: int,
                          user: m.User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    # TODO - implement
    pass


@router.post("/{e_id}/workdays", status_code=status.HTTP_201_CREATED,
             response_model=sc.WorkdayResponse)
def employee_create_workday(e_id: int,
                            workday_data: sc.WorkdayCreate,
                            user: m.User = Depends(get_current_user),
                            db: Session = Depends(get_db)):
    # TODO - implement
    pass

