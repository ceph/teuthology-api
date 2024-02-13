from fastapi.testclient import TestClient
from teuthology_api.main import app
from unittest.mock import patch
from teuthology_api.services.helpers import get_token
from teuthology_api.services.suite import make_run_name, get_run_details
import json

client = TestClient(app)


async def override_get_token():
    return {"access_token": "token_123", "token_type": "bearer"}


app.dependency_overrides[get_token] = override_get_token

mock_suite_args = {
    "--dry-run": False,
    "--non-interactive": False,
    "--verbose": 1,
    "--help": False,
    "--timestamp": "2023-10-21_14:30:00",
    "--owner": "user1",
    "--suite": "rados",
    "--ceph": "ceph1",
    "--kernel": "kernel1",
    "--flavor": "test-flavor",
    "--machine-type": "testnode",
}

# suite
@patch("teuthology_api.services.suite.logs_run")
@patch("teuthology_api.routes.suite.get_username")
@patch("teuthology_api.services.suite.get_run_details")
def test_suite_run_success(m_get_run_details, m_get_username, m_logs_run):
    m_get_username.return_value = "user1"
    m_get_run_details.return_value = {"id": "7451978", "user": "user1"}
    response = client.post("/suite", data=json.dumps(mock_suite_args))
    assert response.status_code == 200
    assert response.json() == {"run": {"id": "7451978", "user": "user1"}}


# make_run_name


def test_make_run_name():
    m_run_dic = {
        "user": "testuser",
        "timestamp": "2022-03-21_14:30:00",
        "suite": "rados",
        "ceph_branch": "ceph1",
        "kernel_branch": "kernel1",
        "flavor": "test-flavor",
        "machine_type": "test-machine",
    }
    expected = (
        "testuser-2022-03-21_14:30:00-rados-ceph1-kernel1-test-flavor-test-machine"
    )
    assert make_run_name(m_run_dic) == expected


def test_make_run_name_with_single_worker():
    m_run_dic = {
        "user": "test_user",
        "timestamp": "2022-03-21_14:30:00",
        "suite": "rados",
        "ceph_branch": "ceph1",
        "kernel_branch": "kernel1",
        "flavor": "test-flavor",
        "machine_type": "worker1",
    }
    expected = "test_user-2022-03-21_14:30:00-rados-ceph1-kernel1-test-flavor-worker1"
    assert make_run_name(m_run_dic) == expected


def test_make_run_name_with_multi_worker():
    m_run_dic = {
        "user": "test_user",
        "timestamp": "2022-03-21_14:30:00",
        "suite": "rados",
        "ceph_branch": "ceph1",
        "kernel_branch": "kernel1",
        "flavor": "test-flavor",
        "machine_type": "worker1,worker2,worker3",
    }
    expected = "test_user-2022-03-21_14:30:00-rados-ceph1-kernel1-test-flavor-multi"
    assert make_run_name(m_run_dic) == expected


def test_make_run_name_with_no_kernel_branch():
    m_run_dic = {
        "user": "teuthology",
        "timestamp": "2022-03-21_14:30:00",
        "suite": "rados",
        "ceph_branch": "ceph1",
        "kernel_branch": None,
        "flavor": "test-flavor",
        "machine_type": "test-machine",
    }
    expected = (
        "teuthology-2022-03-21_14:30:00-rados-ceph1-distro-test-flavor-test-machine"
    )
    assert make_run_name(m_run_dic) == expected
