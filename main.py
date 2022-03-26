import os
import secrets
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from dependencies import get_db
from data import schemas as sc
from data.models import Base, User
from auth import authenticate_user, token_exception, create_access_token, get_password_hash
from data.database import SessionLocal, engine

# Base.metadata.create_all(bind=engine)
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, os.environ.get("API_DOCS_USERNAME"))
    correct_password = secrets.compare_digest(credentials.password, os.environ.get("API_DOCS_PASSWORD"))
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Swagger")


@app.get("/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(get_current_username)):
    return get_openapi(title=app.title, version=app.version, routes=app.routes)


@app.post("/user")
async def create_new_user(user: sc.UserCreate, db: Session = Depends(get_db),
                          username: str = Depends(get_current_username)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    else:
        hashed_password = get_password_hash(user.password)
        db_user = User(username=user.username,
                       hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return db_user


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):

    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:

        raise token_exception()
    token_expires = timedelta()
    access_token = create_access_token(user.username,
                                       user.id,
                                       expires_delta=token_expires)
    return {"access_token": access_token}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
