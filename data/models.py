from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DATE
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    harvests = relationship("Harvest", back_populates="owner")


class Harvest(Base):
    __tablename__ = "harvests"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    start_date = Column(DATE, nullable=False)
    end_date = Column(DATE)
    fruit = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")
