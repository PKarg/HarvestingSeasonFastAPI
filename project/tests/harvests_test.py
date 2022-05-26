from pytest import fixture
from requests import Session
from fastapi.testclient import TestClient

from project.main import app
from .seasons_test import create_season, create_harvest, create_employee, create_season_fix

client: Session = TestClient(app)


# TODO
def test_harvests_get_all():
    pass


# TODO
def test_harvests_get_all_fail_unauthorized():
    pass


# TODO
def test_harvests_get_query_params():
    pass


# TODO
def test_harvests_get_fail_query_params():
    pass


# TODO
def test_harvests_get_by_id():
    pass


# TODO
def test_harvests_get_by_id_fail():
    pass


# TODO
def test_harvests_delete():
    pass


# TODO
def test_harvests_delete_fail():
    pass


# TODO
def test_harvests_patch():
    pass


# TODO
def test_harvests_patch_fail():
    pass


# TODO
def test_harvests_get_employees_all():
    pass


# TODO
def test_harvests_get_employees_query_params():
    pass


# TODO
def test_harvests_get_employees_query_params_fail():
    pass
