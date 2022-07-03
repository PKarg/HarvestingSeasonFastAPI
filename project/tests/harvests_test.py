import datetime

import pytest
from pytest import fixture
from requests import Session
from fastapi.testclient import TestClient

from project.main import app
from .seasons_test import create_season, create_harvest, create_employee, create_season_fix

from .main_test import client, create_user_and_get_token

# TODO expand test suite

def test_harvests_get_all(create_user_and_get_token):
    oauth_header = create_user_and_get_token
    season_a = create_season(oauth_header, start_date=datetime.date(2777, 5, 17)).json()
    season_b = create_season(oauth_header, start_date=datetime.date(2778, 6, 3)).json()
    create_harvest(oauth_header, season_a['year'],
                   date=datetime.date(season_a['year'], 7, 17),
                   fruit="raspberry", harvested=500, price=5)
    create_harvest(oauth_header, season_a['year'],
                   date=datetime.date(season_a['year'], 7, 18),
                   fruit="raspberry", harvested=500, price=5)
    create_harvest(oauth_header, season_a['year'],
                   date=datetime.date(season_a['year'], 7, 19),
                   fruit="raspberry", harvested=500, price=5)
    create_harvest(oauth_header, season_b['year'],
                   date=datetime.date(season_b['year'], 6, 17),
                   fruit="raspberry", harvested=500, price=5)
    create_harvest(oauth_header, season_b['year'],
                   date=datetime.date(season_b['year'], 6, 18),
                   fruit="raspberry", harvested=500, price=5)
    create_harvest(oauth_header, season_b['year'],
                   date=datetime.date(season_b['year'], 6, 19),
                   fruit="raspberry", harvested=500, price=5)
    response = client.get(url="/harvests", headers=oauth_header, allow_redirects=True)
    assert response.status_code == 200
    assert type(response.json()) == list
    assert len(response.json()) == 6


def test_harvests_get_all_fail_unauthorized():
    response = client.get(url="/harvests", headers={}, allow_redirects=True)
    assert response.status_code == 401


@pytest.mark.parametrize('endpoint,status', [('/harvests', 401), ('/harvests/1', 401),
                                             ('/harvests/1/employees', 401), ('/harvests/1/workdays', 401),
                                             ('/harvests/1/summary', 401), ('/harvests/1/employees-summary', 401)])
def test_harvests_fail_unauthorized_gets(endpoint, status):
    response = client.get(url=endpoint, headers={}, allow_redirects=True)
    assert response.status_code == status


@pytest.mark.parametrize('endpoint,status', [('/harvests/1/workdays', 401)])
def test_harvests_fail_unauthorized_post(endpoint, status):
    response = client.post(url=endpoint, headers={}, allow_redirects=True)
    assert response.status_code == status


@pytest.mark.parametrize('endpoint,status', [('/harvests/1', 401)])
def test_harvests_fail_unauthorized_delete(endpoint, status):
    response = client.delete(url=endpoint, headers={}, allow_redirects=True)
    assert response.status_code == status


@pytest.mark.parametrize('endpoint,status', [('/harvests/1', 401)])
def test_harvests_fail_unauthorized_patch(endpoint, status):
    response = client.patch(url=endpoint, headers={}, allow_redirects=True)
    assert response.status_code == status


def test_harvests_get_all_query_params(create_user_and_get_token):
    oauth_header = create_user_and_get_token
    season_a = create_season(oauth_header, start_date=datetime.date(2577, 5, 17)).json()
    season_b = create_season(oauth_header, start_date=datetime.date(2778, 6, 3)).json()

    # HARVESTS FOR SEASON A -----------------------------------
    create_harvest(oauth_header, season_a['year'],
                   date=datetime.date(season_a['year'], 7, 17),
                   fruit="raspberry", harvested=500, price=5)
    create_harvest(oauth_header, season_a['year'],
                   date=datetime.date(season_a['year'], 7, 18),
                   fruit="raspberry", harvested=500, price=5)
    create_harvest(oauth_header, season_a['year'],
                   date=datetime.date(season_a['year'], 7, 19),
                   fruit="raspberry", harvested=500, price=5)
    create_harvest(oauth_header, season_a['year'],
                   date=datetime.date(season_a['year'], 7, 20),
                   fruit="raspberry", harvested=500, price=5)
    # HARVESTS FOR SEASON B -----------------------------------
    create_harvest(oauth_header, season_a['year'],
                   date=datetime.date(season_b['year'], 7, 17),
                   fruit="raspberry", harvested=500, price=5)
    create_harvest(oauth_header, season_a['year'],
                   date=datetime.date(season_b['year'], 7, 18),
                   fruit="raspberry", harvested=500, price=5)
    create_harvest(oauth_header, season_a['year'],
                   date=datetime.date(season_b['year'], 7, 19),
                   fruit="raspberry", harvested=500, price=5)
    create_harvest(oauth_header, season_a['year'],
                   date=datetime.date(season_b['year'], 7, 20),
                   fruit="raspberry", harvested=500, price=5)
