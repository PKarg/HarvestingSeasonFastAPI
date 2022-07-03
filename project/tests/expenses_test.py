import pytest
from pytest import fixture

from .main_test import client, create_user_and_get_token

# TODO expand test suite


@pytest.mark.parametrize('endpoint,status', [('/expenses', 401), ('/expenses/1', 401)])
def test_expenses_fail_unauthorized_gets(endpoint, status):
    response = client.get(url=endpoint, headers={}, allow_redirects=True)
    assert response.status_code == status


@pytest.mark.parametrize('endpoint,status', [('/expenses/1', 401)])
def test_expenses_fail_unauthorized_delete(endpoint, status):
    response = client.delete(url=endpoint, headers={}, allow_redirects=True)
    assert response.status_code == status


@pytest.mark.parametrize('endpoint,status', [('/expenses/1', 401)])
def test_expenses_fail_unauthorized_patch(endpoint, status):
    response = client.patch(url=endpoint, headers={}, allow_redirects=True)
    assert response.status_code == status
