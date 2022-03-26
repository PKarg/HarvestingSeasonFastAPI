from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from data.models import Base
from data.database import SessionLocal, engine

# Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
