from fastapi.testclient import TestClient
from fastapi import HTTPException
import pytest
from teuthology_api.main import app
from unittest.mock import patch
from teuthology_api.services.helpers import Request, get_token, get_username

client = TestClient(app)

# Expected 401 detail when no auth (matches helpers.resolve_access_token)
AUTH_REQUIRED_DETAIL = (
    "You need to be logged in. Use X-Access-Token header, "
    "Authorization: Bearer header, or browser login."
)


class MockRequest:
    """Minimal request-like object for resolve_access_token (session + headers)."""

    def __init__(self, access_token="testToken123", bad=False):
        # resolve_access_token checks headers first, then session
        self.headers = {}  # no Authorization / X-Access-Token, so it falls back to session
        if bad:
            self.session = {}
        else:
            self.session = {
                "user": {
                    "username": "user1",
                    "access_token": access_token,
                }
            }


# get_token (async)
@patch("teuthology_api.services.helpers.Request")
@pytest.mark.asyncio
async def test_get_token_success(m_request):
    m_request = MockRequest()
    expected = {"access_token": "testToken123", "token_type": "bearer"}
    actual = await get_token(m_request)
    assert expected == actual


@patch("teuthology_api.services.helpers.Request")
@pytest.mark.asyncio
async def test_get_token_fail(m_request):
    with pytest.raises(HTTPException) as err:
        m_request = MockRequest(bad=True)
        await get_token(m_request)
    assert err.value.status_code == 401
    assert err.value.detail == AUTH_REQUIRED_DETAIL


# get_username (async)
@patch("teuthology_api.services.helpers.Request")
@pytest.mark.asyncio
async def test_get_username_success(m_request):
    m_request = MockRequest()
    expected = "user1"
    actual = await get_username(m_request)
    assert expected == actual


@patch("teuthology_api.services.helpers.Request")
@pytest.mark.asyncio
async def test_get_username_fail(m_request):
    with pytest.raises(HTTPException) as err:
        m_request = MockRequest(bad=True)
        await get_username(m_request)
    assert err.value.status_code == 401
    assert err.value.detail == AUTH_REQUIRED_DETAIL
