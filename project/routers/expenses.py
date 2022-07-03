import os
from typing import List, Optional

from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks
from starlette.responses import FileResponse

from project.auth import get_current_active_user
from project.data import models as m, schemas as sc
from project.dependencies import get_db, order_by_query
from . import crud
from ..additional import create_temp_csv, delete_temp_files

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"]
)


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[sc.ExpenseResponse])
def expense_get_all(background_tasks: BackgroundTasks,
                    user: m.User = Depends(get_current_active_user),
                    db: Session = Depends(get_db),
                    type: Optional[str] = Query(None, min_length=2, max_length=30, regex=r"[a-zA-Z]+"),
                    after: Optional[str] = Query(None, min_length=10, max_length=10, regex=r"^[0-9]+(-[0-9]+)+$"),
                    before: Optional[str] = Query(None, min_length=10, max_length=10, regex=r"^[0-9]+(-[0-9]+)+$"),
                    order_by_qp=Depends(order_by_query),
                    more: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                    less: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                    season_id: Optional[str] = Query(None, regex=r"^ *\d[\d ]*$"),
                    data_format: Optional[str] = Query('json', min_length=3, max_length=4)):
    if data_format not in ('json', 'csv'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Data format must be 'json' or 'csv', not '{data_format}'")
    expenses = crud.expenses_get(db=db, user=user, season_id=season_id, type=type, after=after,
                             before=before, more=more, less=less, **order_by_qp)
    if data_format == 'csv':
        e_data = [dict((col, getattr(e, col)) for col in e.__table__.columns.keys()) for e in expenses]
        filename = f"user_{user.username}_{user.id}_expenses"
        compressed_file, tmp_dir = create_temp_csv(data=e_data,
                                                   filename=filename,
                                                   column_names=[k for k in e_data[0].keys()])
        background_tasks.add_task(delete_temp_files, tmp_dir)
        return FileResponse(path=os.path.join(tmp_dir, compressed_file), filename=compressed_file,
                            media_type='application/zip')
    return expenses


@router.get("/{ex_id}", status_code=status.HTTP_200_OK,
            response_model=sc.ExpenseResponse)
def expense_get_id(ex_id: int,
                   user: m.User = Depends(get_current_active_user),
                   db: Session = Depends(get_db)):
    return crud.expenses_get(db=db, user=user, id=ex_id)[0]


@router.patch("/{ex_id}", status_code=status.HTTP_200_OK,
              response_model=sc.ExpenseResponse)
def expense_update(ex_id: int,
                   expense_data: sc.ExpenseUpdate,
                   user: m.User = Depends(get_current_active_user),
                   db: Session = Depends(get_db)):
    return crud.expense_update(db=db, id=ex_id, user=user, data=expense_data)


@router.delete("/{e_id}", status_code=status.HTTP_200_OK)
def expense_update(ex_id: int,
                   user: m.User = Depends(get_current_active_user),
                   db: Session = Depends(get_db)):
    expense_to_delete = crud.expenses_get(db=db, user=user, id=ex_id)[0]
    db.delete(expense_to_delete)
    db.commit()
