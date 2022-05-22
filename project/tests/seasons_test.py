from pytest import fixture
import requests
from fastapi.testclient import TestClient

from project.main import app
from .main_test import create_user_and_get_token


client: requests.Session = TestClient(app)


def test_season_create_no_end_date(create_user_and_get_token):
    oauth_header = create_user_and_get_token
    body = {"start_date": "2777-05-22"}
    response = client.post(url="/seasons", json=body,
                           headers=oauth_header, allow_redirects=True)
    assert response.status_code == 201
    assert response.json()['start_date'] == "2777-05-22"
    assert response.json()['year'] == 2777
    assert response.json()['end_date'] is None


def test_season_create_end_date(create_user_and_get_token):
    oauth_header = create_user_and_get_token
    body = {"start_date": "2777-05-22", "end_date": "2777-09-22"}
    response = client.post(url="/seasons", json=body,
                           headers=oauth_header, allow_redirects=True)
    assert response.status_code == 201
    assert response.json()['end_date'] == "2777-09-22"

@fixture
def create_season(create_user_and_get_token):
    oauth_header = create_user_and_get_token
    body = {"start_date": "2777-05-22"}
    response = client.post(url="/seasons", json=body,
                           headers=oauth_header, allow_redirects=True)
