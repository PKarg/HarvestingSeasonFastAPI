from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from auth import get_current_user
from data import models as m, schemas as sc
from dependencies import get_db
from . import crud

router = APIRouter(
    prefix="/seasons",
    tags=["seasons"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def seasons_post(season_data: sc.SeasonBase,
                 user: m.User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    return crud.season_create(db, user, season_data.start_date, season_data.end_date)


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[sc.SeasonResponse])
def seasons_get_all(user: m.User = Depends(get_current_user),
                    db: Session = Depends(get_db),
                    after: Optional[str] = Query(None, min_length=10, max_length=10, regex=r"^[0-9]+(-[0-9]+)+$"),
                    before: Optional[str] = Query(None, min_length=10, max_length=10, regex=r"^[0-9]+(-[0-9]+)+$"),
                    limit: Optional[str] = None,
                    offset: Optional[str] = None):
    return crud.season_get(db=db, user=user, after=after, before=before,
                           limit=limit, offset=offset)


@router.get("/{year}", status_code=status.HTTP_200_OK,
            response_model=sc.SeasonResponse)
def seasons_get_by_year(year: int,
                        user: m.User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    return crud.season_get(db, user, year)[0]


@router.patch("/{year}", status_code=status.HTTP_200_OK,
              response_model=sc.SeasonResponse)
def seasons_update(year: int, season_data: sc.SeasonUpdate,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    season_m = crud.season_get(db, user, year)[0]
    return crud.season_update(db, season_m, season_data.start_date, season_data.end_date)


@router.delete("/{year}", status_code=status.HTTP_200_OK)
def seasons_update(year: int,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    season_m = crud.season_get(db, user, year)[0]
    db.delete(season_m)
    db.commit()


@router.post("/{year}/harvests", status_code=status.HTTP_201_CREATED,
             response_model=sc.HarvestResponseEmployees)
def harvests_post(year: int,
                  harvest_data: sc.HarvestCreate,
                  user: m.User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    return crud.harvest_create(db, user, year, harvest_data)


@router.get("/{year}/harvests", status_code=status.HTTP_200_OK,
            response_model=List[sc.HarvestResponse])
def harvests_get(year: int,
                 user: m.User = Depends(get_current_user),
                 db: Session = Depends(get_db),
                 after: Optional[str] = Query(None, min_length=10, max_length=10, regex=r"^[0-9]+(-[0-9]+)+$"),
                 before: Optional[str] = Query(None, min_length=10, max_length=10, regex=r"^[0-9]+(-[0-9]+)+$"),
                 fruit: Optional[str] = Query(None, min_length=3, max_length=30),
                 p_more: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                 p_less: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                 h_more: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                 h_less: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$")):
    return crud.harvests_get(db, user, year=year, after=after, before=before,
                            fruit=fruit, p_more=p_more, p_less=p_less, h_more=h_more, h_less=h_less)


@router.post("/{year}/employees", status_code=status.HTTP_201_CREATED,
             response_model=sc.EmployeeResponseHarvests)
def employees_post(year: int,
                   employee_data: sc.EmployeeCreate,
                   user: m.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    return crud.employee_create(db=db, user=user, year=year, data=employee_data)


@router.get("{year}/employees", status_code=status.HTTP_200_OK,
            response_model=List[sc.EmployeeResponse])
def employees_get(year: int,
                  user: m.User = Depends(get_current_user),
                  db: Session = Depends(get_db),
                  after: Optional[str] = Query(None, min_length=10, max_length=10, regex=r"^[0-9]+(-[0-9]+)+$"),
                  before: Optional[str] = Query(None, min_length=10, max_length=10, regex=r"^[0-9]+(-[0-9]+)+$"),
                  name: Optional[str] = Query(None, min_length=2, max_length=10, regex=r"[a-zA-Z]+")):
    return crud.employees_get(db=db, user=user, year=year, after=after, before=before, name=name)


@router.post("/{year}/expenses", status_code=status.HTTP_201_CREATED,
             response_model=sc.ExpenseResponse)
def expenses_post(year: int,
                  expense_data: sc.ExpenseCreate,
                  user: m.User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    return crud.expense_create(db=db, year=year, user=user, data=expense_data)


@router.get("/{year}/expenses", status_code=status.HTTP_200_OK,
            response_model=List[sc.ExpenseResponse])
def expenses_get(year: int,
                 user: m.User = Depends(get_current_user),
                 db: Session = Depends(get_db),
                 type: Optional[str] = Query(None, min_length=2, max_length=30, regex=r"[a-zA-Z]+"),
                 after: Optional[str] = Query(None, min_length=10, max_length=10, regex=r"^[0-9]+(-[0-9]+)+$"),
                 before: Optional[str] = Query(None, min_length=10, max_length=10, regex=r"^[0-9]+(-[0-9]+)+$"),
                 more: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                 less: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$")):
    return crud.expenses_get(db=db, user=user, year=year, type=type, after=after, before=before, more=more, less=less)
