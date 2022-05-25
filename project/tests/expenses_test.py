from pytest import fixture
from requests import Session
from fastapi.testclient import TestClient

from project.main import app


client: Session = TestClient(app)