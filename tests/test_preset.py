from unittest.mock import patch
from urllib.parse import urlencode

from fastapi.testclient import TestClient
from sqlmodel import Session

preset_payload = {
    "name": "test",
    "suite": "teuthology:no-ceph",
    "cmd": {
        "--suite": "teuthology:no-ceph",
        "--owner": "user1",
    },
}


@patch("teuthology_api.routes.presets.get_username")
def test_create_preset(m_get_username, session: Session, client: TestClient):
    m_get_username.return_value = "user1"
    response = client.post("/presets/add", json=preset_payload)
    assert response.status_code == 201


def test_get_preset_by_name(session: Session, client: TestClient):
    params = {"username": "user1", "name": "test"}
    response = client.get(f"/presets?{urlencode(params)}")
    data = response.json()

    assert response.status_code == 200
    assert data["username"] == "user1"
    assert data["name"] == "test"


def test_get_all_presets(session: Session, client: TestClient):
    params = {"username": "user1"}
    response = client.get(f"/presets/list?{urlencode(params)}")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1


def test_update_preset(session: Session, client: TestClient):
    preset_payload["name"] = "test-updated"
    response = client.put("/presets/edit/1", json=preset_payload)
    data = response.json()

    assert response.status_code == 200
    assert data["username"] == "user1"
    assert data["name"] == "test-updated"


def test_delete_preset(session: Session, client: TestClient):
    response = client.delete("/presets/delete/1")
    assert response.status_code == 204
