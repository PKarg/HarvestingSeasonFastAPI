from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import project.data.models as m
from project.dependencies import get_db
from project.auth import check_if_user_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.delete("/seasons/", status_code=status.HTTP_200_OK)
def delete_all_seasons_admin(db: Session = Depends(get_db),
                             user: m.User = Depends(check_if_user_admin)):
    db.query(m.Season).delete()


@router.delete("/seasons/{s_id}", status_code=status.HTTP_200_OK)
def delete_season_admin(s_id: int,
                        db: Session = Depends(get_db),
                        user: m.User = Depends(check_if_user_admin)):
    season_m = db.query(m.Season).filter(m.Season.id == s_id).first()
    db.delete(season_m)
    db.commit()


@router.get("/seasons/", status_code=status.HTTP_200_OK)
def get_all_seasons_admin(user: m.User = Depends(check_if_user_admin),
                          db: Session = Depends(get_db)):
    return db.query(m.Season).all()
