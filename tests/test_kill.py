from fastapi.testclient import TestClient
from teuthology_api.main import app
from unittest.mock import patch
from teuthology_api.services.helpers import get_token
from teuthology_api.services.kill import get_username, get_run_details
import json
from teuthology_api.schemas.kill import KillArgs

client = TestClient(app)


async def override_get_token():
    return {"access_token": "token_123", "token_type": "bearer", "isUserAdmin": False}


app.dependency_overrides[get_token] = override_get_token

mock_kill_args = {
    "--dry-run": False,
    "--non-interactive": False,
    "--verbose": 1,
    "--help": False,
    "--owner": "user1",
    "--run": "mock_run",
    "--preserve-queue": None,
    "--job": None,
    "--jobspec": None,
    "--machine-type": "testnode",
    "--archive": None,
}


@patch("teuthology_api.services.kill.isAdmin")
@patch("subprocess.Popen")
@patch("teuthology_api.services.kill.get_run_details")
@patch("teuthology_api.services.kill.get_username")
def test_kill_run_success(m_get_username, m_get_run_details, m_popen, m_isAdmin):
    m_get_username.return_value = "user1"
    m_isAdmin.return_value = False
    m_get_run_details.return_value = {
        "id": "7451978",
        "user": "user1",
        "jobs": [{"owner": "user1"}],
    }
    mock_process = m_popen.return_value
    mock_process.communicate.return_value = (b"logs", "")
    mock_process.wait.return_value = 0
    response = client.post("kill/", data=json.dumps(mock_kill_args))
    assert response.status_code == 200
    assert response.json() == {"kill": "success"}


def test_kill_run_fail():
    response = client.post("/kill", data=json.dumps(mock_kill_args))
    assert response.status_code == 401
    assert response.json() == {"detail": "You need to be logged in"}


@patch("teuthology_api.services.kill.isAdmin")
@patch("subprocess.Popen")
@patch("teuthology_api.services.kill.get_run_details")
@patch("teuthology_api.services.kill.get_username")
def test_admin_kill_run_success(m_get_username, m_get_run_details, m_popen, m_isAdmin):
    m_get_username.return_value = "user1"
    m_isAdmin.return_value = True
    m_get_run_details.return_value = {
        "id": "7451978",
        "user": "user1",
        "jobs": [{"owner": "someone_else"}],
    }
    mock_process = m_popen.return_value
    mock_process.communicate.return_value = (b"logs", "")
    mock_process.wait.return_value = 0
    response = client.post("kill/", data=json.dumps(mock_kill_args))
    assert response.status_code == 200
    assert response.json() == {"kill": "success"}


@patch("teuthology_api.services.kill.isAdmin")
@patch("subprocess.Popen")
@patch("teuthology_api.services.kill.get_run_details")
@patch("teuthology_api.services.kill.get_username")
def test_non_admin_kill_run_fail(m_get_username, m_get_run_details, m_popen, m_isAdmin):
    m_get_username.return_value = "user1"
    m_isAdmin.return_value = False
    m_get_run_details.return_value = {
        "id": "7451978",
        "user": "user1",
        "jobs": [{"owner": "someone_else"}],
    }
    mock_process = m_popen.return_value
    mock_process.communicate.return_value = (b"logs", "")
    mock_process.wait.return_value = 0
    response = client.post("kill/", data=json.dumps(mock_kill_args))
    assert response.status_code == 401  # run doesn't belong to user + user is not admin
