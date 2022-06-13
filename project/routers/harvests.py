from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from project.auth import get_current_active_user
from project.data import models as m, schemas as sc
from project.dependencies import get_db, after_before, price_harvested_more_less, limit_offset
from . import crud

router = APIRouter(
    prefix="/harvests",
    tags=["harvests"]
)


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[sc.HarvestResponseALL])
def harvests_get_all(user: m.User = Depends(get_current_active_user),
                     db: Session = Depends(get_db),
                     year: Optional[str] = Query(None, min_length=4, max_length=4, regex=r"^ *\d[\d ]*$"),
                     season_id: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                     fruit: Optional[str] = Query(None, min_length=5, max_length=20),
                     after_before_qp=Depends(after_before),
                     price_harvested_qp=Depends(price_harvested_more_less),
                     limit_offset_qp=Depends(limit_offset)):
    return crud.harvests_get(db, user, fruit=fruit, year=year, season_id=season_id,
                             **after_before_qp, **price_harvested_qp, **limit_offset_qp)


@router.get("/{h_id}", status_code=status.HTTP_200_OK,
            response_model=sc.HarvestResponseALL)
def harvests_get_id(h_id: int,
                    user: m.User = Depends(get_current_active_user),
                    db: Session = Depends(get_db)):
    try:
        return crud.harvests_get(db, user, id=h_id)[0]
    except IndexError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object with given id doesn't exist")


@router.delete("/{h_id}", status_code=status.HTTP_200_OK,
               response_model=None)
def harvests_delete(h_id: int,
                    user: m.User = Depends(get_current_active_user),
                    db: Session = Depends(get_db)):
    harvest_m = crud.harvests_get(db, user, id=h_id)[0]
    db.delete(harvest_m)
    db.commit()


@router.patch("/{h_id}", status_code=status.HTTP_200_OK,
              response_model=sc.HarvestResponse)
def harvests_update(h_id: int,
                    harvest_data: sc.HarvestUpdate,
                    user: m.User = Depends(get_current_active_user),
                    db: Session = Depends(get_db)):
    harvest_m_updated = crud.harvest_update(db=db, user=user, id=h_id, data=harvest_data)
    return harvest_m_updated


@router.get("/{h_id}/employees", status_code=status.HTTP_200_OK,
            response_model=List[sc.EmployeeResponse])
def harvests_get_employees(h_id: int,
                           user: m.User = Depends(get_current_active_user),
                           db: Session = Depends(get_db),
                           after_before_qp=Depends(after_before),
                           limit_offset_qp=Depends(limit_offset),
                           name: Optional[str] = Query(None, min_length=2, max_length=10, regex=r"[a-zA-Z]+")):
    return crud.employees_get(db=db, user=user, harvest_id=h_id, name=name, **after_before_qp, **limit_offset_qp)


@router.get("/{id}/workdays", status_code=status.HTTP_200_OK,
            response_model=List[sc.WorkdayResponse])
def harvests_get_workdays(h_id: int,
                          user: m.User = Depends(get_current_active_user),
                          db: Session = Depends(get_db),
                          fruit: Optional[str] = Query(None, min_length=5, max_length=20),
                          price_harvested_qp=Depends(price_harvested_more_less),
                          limit_offset_qp=Depends(limit_offset)):
    return crud.workdays_get(db=db, user=user, h_id=h_id,
                             fruit=fruit, **price_harvested_qp, **limit_offset_qp)


@router.post("/{id}/workdays", status_code=status.HTTP_201_CREATED,
             response_model=sc.WorkdayResponse)
def harvests_post_workday(h_id: int,
                          workday_data: sc.WorkdayCreate,
                          user: m.User = Depends(get_current_active_user),
                          db: Session = Depends(get_db)):
    return crud.workday_create(db=db, user=user, data=workday_data, h_id=h_id)


@ router.get("/{id}/summary", status_code=status.HTTP_200_OK)
def harvests_get_summary(h_id: int,
                         user: m.User = Depends(get_current_active_user),
                         db: Session = Depends(get_db),
                         sumfor: Optional[str] = Query("json", max_length=4, examples={"format": "json"})):
    harvest = crud.harvests_get(db, user=user, id=h_id)[0]

    har_per_emp = {w.employee.name: (round(float(w.harvested), 2),
                                     round(float(w.pay_per_kg), 2),
                                     round(float(w.harvested * w.pay_per_kg), 2)) for w in harvest.workdays}
    harvested_max = max([round(float(w.harvested), 2) for w in harvest.workdays])
    best_emp = next(({emp: har} for emp, har in har_per_emp.items() if har[0] == harvested_max), None)
    harvested_by_employees = sum([w.harvested for w in harvest.workdays])
    avg_pay_per_kg = sum([w.pay_per_kg for w in harvest.workdays])/len(harvest.workdays)
    harvest.print_employees()

    report = {
        "date": harvest.date,
        "fruit": harvest.fruit,
        "harvested_all": harvest.harvested,
        "harvested_by_employees": harvest.harvested_by_employees(),
        "price_per_kg": harvest.price,
        "avg_pay_per_kg": harvest.avg_pay_per_kg(),
        "total_profits": harvest.total_profits(),
        "harvested_by_emp_profits": harvested_by_employees * harvest.price,
        "total_paid": harvested_by_employees * avg_pay_per_kg,
        "net_profit": harvest.net_profit(),
        "best_employee": best_emp,
        "harvested_per_emp": har_per_emp
    }

    return report
