import os

import requests
import sqlalchemy.orm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from pytest import fixture

from project.main import app
from project.dependencies import get_db
import project.data.models as m

# TESTING DB
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine_test = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

m.Base.metadata.create_all(bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client: requests.Session = TestClient(app)


def test_hello():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_create_user_and_get_token():
    user_data = {
        "username": "kasztan_test_login",
        "password": "kasztan_test_pass",
        "active": True,
        "auth_level": 1
    }
    try:
        response = client.post(url="/user", json=user_data, auth=('admin', 'admin'))
        print(response.json())
        assert response.status_code == 201

        response = client.post(url="/token", data=user_data)
        assert response.status_code == 200
        assert "access_token" in response.json()
    finally:
        db: sqlalchemy.orm.Session = next(override_get_db())
        user_m: m.User = db.query(m.User).filter(m.User.username == user_data['username']).first()
        db.delete(user_m)
        db.commit()


@fixture
def create_user_and_get_token():
    user_data = {
        "username": "kasztan_test_login",
        "password": "kasztan_test_pass",
        "active": True,
        "auth_level": 1
    }
    # Create test user
    response = client.post(url="/user", json=user_data,
                           auth=(os.environ.get("API_DOCS_USERNAME"),
                                 os.environ.get("API_DOCS_PASSWORD")))
    assert response.status_code == 201

    response = client.post(url="/token", data=user_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

    yield {"Authorization": f"Bearer {response.json()['access_token']}"}

    db: sqlalchemy.orm.Session = next(override_get_db())
    user_m: m.User = db.query(m.User).filter(m.User.username == user_data['username']).first()
    db.delete(user_m)
    db.commit()
