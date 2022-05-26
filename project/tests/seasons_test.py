import datetime
from typing import Tuple, Optional, List

from pytest import fixture
from requests import Session
from fastapi.testclient import TestClient

from project.main import app
from .main_test import create_user_and_get_token


client: Session = TestClient(app)


def create_harvest(oauth_header: dict, s_year: int, price: int,
                   harvested: int, date: datetime.date, fruit: Optional[str] = None,
                   employee_ids: Optional[List] = None):
    body = {
        "price": price,
        "harvested": harvested,
        "date": date.isoformat(),
        "fruit": fruit,
        "employee_ids": employee_ids if employee_ids else None
    }
    response = client.post(url=f"/seasons/{s_year}/harvests", json=body,
                           headers=oauth_header, allow_redirects=True)
    return response


def create_employee(oauth_header: dict, s_year: int, name: Optional[str] = None,
                    start_date: Optional[datetime.date] = None,
                    end_date: Optional[datetime.date] = None,
                    harvest_ids: Optional[List] = None):
    body = {
        "name": name,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat() if end_date else None,
        "harvest_ids": harvest_ids if harvest_ids else None
    }
    response = client.post(url=f"/seasons/{s_year}/employees", json=body,
                           headers=oauth_header, allow_redirects=True)
    return response


def create_season(oauth_header: dict, start_date: Optional[datetime.date] = None,
                  end_date: Optional[datetime.date] = None):
    body = {"start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None}
    response = client.post(url="/seasons", json=body,
                           headers=oauth_header, allow_redirects=True)
    return response


@fixture
def create_season_fix(create_user_and_get_token) -> Tuple[dict, dict]:
    oauth_header = create_user_and_get_token
    season = create_season(oauth_header=oauth_header, start_date=datetime.date(2777, 5, 22),
                           end_date=datetime.date(2777, 9, 22))
    yield oauth_header, season.json()


@fixture
def create_harvest_fix(create_season_fix):
    oauth_header, season = create_season_fix
    response = create_harvest(oauth_header=oauth_header,
                              s_year=season['year'],
                              fruit="raspberry",
                              harvested=666,
                              price=6, date=datetime.date(2777, 6, 11))
    yield oauth_header, season, response.json()


@fixture
def create_employee_fix(create_season_fix):
    oauth_header, season = create_season_fix
    response = create_employee(oauth_header, s_year=season['year'],
                               name="Kasztan",
                               start_date=datetime.date(2777, 5, 28),
                               end_date=datetime.date(2777, 9, 14))
    yield oauth_header, season, response.json()


def test_season_create_no_end_date(create_user_and_get_token):
    oauth_header = create_user_and_get_token
    response = create_season(oauth_header=oauth_header, start_date=datetime.date(2777, 5, 22))
    assert response.status_code == 201
    assert response.json()['start_date'] == "2777-05-22"
    assert response.json()['year'] == 2777
    assert response.json()['end_date'] is None


def test_season_create_no_start_date(create_user_and_get_token):
    oauth_header = create_user_and_get_token
    response = create_season(oauth_header=oauth_header)
    assert response.status_code == 201
    assert response.json()['start_date'] == datetime.date.today().isoformat()
    assert response.json()['year'] == datetime.date.today().year
    assert response.json()['end_date'] is None


def test_season_create_end_date(create_user_and_get_token):
    oauth_header = create_user_and_get_token
    response = create_season(oauth_header=oauth_header, start_date=datetime.date(2777, 5, 22),
                             end_date=datetime.date(2777, 9, 22))
    assert response.status_code == 201
    assert response.json()['start_date'] == "2777-05-22"
    assert response.json()['end_date'] == "2777-09-22"


def test_season_create_fail_wrong_date(create_user_and_get_token):
    oauth_header = create_user_and_get_token
    response = create_season(oauth_header=oauth_header, start_date=datetime.date(2777, 5, 22),
                             end_date=datetime.date(2777, 4, 22))
    assert response.status_code == 422


def test_season_create_fail_year_exists(create_user_and_get_token):
    oauth_header = create_user_and_get_token
    create_season(oauth_header=oauth_header, start_date=datetime.date(2022, 5, 24),
                  end_date=datetime.date(2022, 8, 13))
    response = create_season(oauth_header=oauth_header, start_date=datetime.date(2022, 5, 12),
                             end_date=datetime.date(2022, 9, 27))
    assert response.status_code == 422


def test_season_create_fail_unauthorized(create_season_fix):
    oauth_header = {"Authorization": "Bearer Kasztan"}
    response = create_season(oauth_header=oauth_header)
    assert response.status_code == 401


def test_seasons_get_all(create_season_fix):
    oauth_header, _ = create_season_fix
    response = client.get("/seasons", headers=oauth_header, allow_redirects=True)
    assert type(response.json()) == list
    assert type(response.json()[0]) == dict


def test_seasons_get_by_year(create_season_fix):
    oauth_header, season = create_season_fix
    response = client.get(f"/seasons/{season['year']}", headers=oauth_header, allow_redirects=True)
    assert response.status_code == 200
    assert type(response.json()) == dict
    assert response.json()['id'] == season['id']
    assert response.json()['year'] == season['year']


def test_season_get_fail_doesnt_exist(create_user_and_get_token):
    oauth_header = create_user_and_get_token
    response = client.get(headers=oauth_header, url="/seasons/7777")
    assert response.status_code == 404


def test_seasons_create_harvest_no_employees(create_season_fix):
    oauth_header, season = create_season_fix
    response = create_harvest(oauth_header=oauth_header, s_year=season['year'],
                              fruit="raspberry", date=datetime.date(2777, 6, 18),
                              harvested=666, price=6)
    assert response.status_code == 201
    assert response.json()['fruit'] == "raspberry"
    assert response.json()['date'] == datetime.date(2777, 6, 18).isoformat()


def test_season_create_harvest_fail_forbidden_fruit(create_season_fix):
    oauth_header, season = create_season_fix
    response = create_harvest(oauth_header=oauth_header, s_year=season['year'],
                              fruit="kasztan", date=datetime.date(season['year'], 7, 16),
                              harvested=123, price=4)
    assert response.status_code == 422


def test_season_create_harvest_fail_date_out_of_bounds(create_season_fix):
    oauth_header, season = create_season_fix
    response = create_harvest(oauth_header, season['year'],
                              date=datetime.date(season['year'], 11, 1),
                              price=12, harvested=123, fruit="raspberry")
    assert response.status_code == 422


def test_season_create_harvest_fail_incomplete_data(create_season_fix):
    oauth_header, season = create_season_fix
    response = create_harvest(oauth_header, season['year'],
                              date=datetime.date(season['year'], 8, 12),
                              harvested=12, price=1, fruit=None)
    assert response.status_code == 422


def test_season_get_harvests_all(create_harvest_fix):
    oauth_header, season, harvest = create_harvest_fix
    response = client.get(url=f"seasons/{season['year']}/harvests", headers=oauth_header)
    assert response.status_code == 200
    assert type(response.json()) is list
    assert type(response.json()[0]) is dict
    assert response.json()[0]['date'] == harvest['date']


def test_season_get_harvests_all_fail_unauthorized(create_season_fix):
    oauth_header, season = create_season_fix
    response = client.get(url=f"seasons/{season['year']}/harvests", headers=())
    assert response.status_code == 401


def test_season_create_employee_no_end_date(create_season_fix):
    oauth_header, season = create_season_fix
    response = create_employee(oauth_header=oauth_header, s_year=season['year'],
                               name="Stefan", start_date=datetime.date(2777, 6, 16))
    assert response.status_code == 201
    assert response.json()
    assert response.json()['name'] == "Stefan"
    assert response.json()['start_date'] == datetime.date(2777, 6, 16).isoformat()


def test_seasons_create_employee_end_date(create_season_fix):
    oauth_header, season = create_season_fix
    response = create_employee(oauth_header=oauth_header, s_year=season['year'],
                               name="Stefan", start_date=datetime.date(2777, 6, 16),
                               end_date=datetime.date(2777, 8, 17))
    assert response.status_code == 201
    assert response.json()
    assert response.json()['name'] == "Stefan"
    assert response.json()['start_date'] == datetime.date(2777, 6, 16).isoformat()
    assert response.json()['end_date'] == datetime.date(2777, 8, 17).isoformat()


def test_season_create_employee_fail_incomplete_data(create_season_fix):
    oauth_header, season = create_season_fix
    response = create_employee(oauth_header=oauth_header, s_year=season['year'],
                               name=None, start_date=datetime.date(2777, 6, 16),
                               end_date=datetime.date(2777, 8, 17))
    assert response.status_code == 422


def test_season_create_employee_fail_incompatible_dates(create_season_fix):
    oauth_header, season = create_season_fix
    response = create_employee(oauth_header=oauth_header, s_year=season['year'],
                               name="Stefan", start_date=datetime.date(2777, 9, 16),
                               end_date=datetime.date(2777, 7, 17))
    assert response.status_code == 422


def test_season_create_employee_fail_dates_out_of_bounds(create_season_fix):
    oauth_header, season = create_season_fix
    response_a = create_employee(oauth_header=oauth_header, s_year=season['year'],
                                 name="Stefan", start_date=datetime.date(2777, 3, 16),
                                 end_date=datetime.date(2777, 7, 17))
    response_b = create_employee(oauth_header=oauth_header, s_year=season['year'],
                                 name="Stefan", start_date=datetime.date(2777, 5, 28),
                                 end_date=datetime.date(2777, 10, 17))
    assert response_a.status_code == 422
    assert response_b.status_code == 422


def test_season_create_harvest_with_employees(create_season_fix):
    oauth_header, season = create_season_fix
    employee = create_employee(oauth_header=oauth_header, s_year=season['year'],
                               name="Stefan", start_date=datetime.date(2777, 5, 27),
                               end_date=datetime.date(2777, 7, 17))
    response = create_harvest(oauth_header, season['year'],
                              date=datetime.date(2777, 6, 12),
                              harvested=12, price=1, fruit="raspberry",
                              employee_ids=[employee.json()['id']])
    assert response.status_code == 201
    assert type(response.json()) is dict
    assert type(response.json()['employees']) is list
    assert type(response.json()['employees'][0]) is dict


# TODO
def test_season_create_harvest_with_employees_fail_incompatible_dates(create_season_fix):
    pass


# TODO
def test_season_create_harvest_with_employees_fail_different_seasons():
    pass


# TODO
def test_season_create_employee_with_harvests():
    pass


# TODO
def test_season_create_employee_with_harvests_fail_incompatible_dates():
    pass


# TODO
def test_season_create_employee_with_harvests_fail_different_seasons():
    pass


# TODO
def test_season_create_expense():
    pass


# TODO
def test_season_create_expense_fail_unauthorized():
    pass


# TODO
def test_season_create_expense_fail_incomplete_data():
    pass


# TODO
def test_season_create_expense_nonexistent_season():
    pass


# TODO
def test_season_get_expense():
    pass


# TODO
def test_season_get_expense_fail_unauthorized():
    pass
