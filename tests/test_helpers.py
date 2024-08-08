from fastapi import HTTPException
import pytest
from unittest.mock import patch
from teuthology_api.services.helpers import get_token, get_username


class MockRequest:
    def __init__(self, access_token="testToken123", bad=False):
        if bad:
            self.session = {}
        else:
            self.session = {
                "user": {
                    "username": "user1",
                    "access_token": access_token,
                }
            }


# get_token
@patch("teuthology_api.services.helpers.Request")
def test_get_token_success(m_request):
    m_request = MockRequest()
    expected = {"access_token": "testToken123", "token_type": "bearer"}
    actual = get_token(m_request)
    assert expected == actual


@patch("teuthology_api.services.helpers.Request")
def test_get_token_fail(m_request):
    with pytest.raises(HTTPException) as err:
        m_request = MockRequest(bad=True)
        get_token(m_request)
    assert err.value.status_code == 401
    assert err.value.detail == "You need to be logged in"


# get username
@patch("teuthology_api.services.helpers.Request")
def test_get_username_success(m_request):
    m_request = MockRequest()
    expected = "user1"
    actual = get_username(m_request)
    assert expected == actual


@patch("teuthology_api.services.helpers.Request")
def test_get_username_fail(m_request):
    with pytest.raises(HTTPException) as err:
        m_request = MockRequest(bad=True)
        get_username(m_request)
    assert err.value.status_code == 401
    assert err.value.detail == "You need to be logged in"
