import logging

from fastapi import APIRouter, HTTPException, Depends, Request

from teuthology_api.services.suite import run
from teuthology_api.services.helpers import get_token, get_username
from teuthology_api.schemas.suite import SuiteArgs

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/suite",
    tags=["suite"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", status_code=200)
def create_run(
    request: Request,
    args: SuiteArgs,
    access_token: str = Depends(get_token),
    logs: bool = False,
):
    args = args.model_dump(by_alias=True)
    args["--user"] = get_username(request)
    return run(args, logs, access_token)


@router.post("/default", status_code=200)
def create_run_default(
    request: Request,
    access_token: str = Depends(get_token),
    logs: bool = False,
):
    args = {
        "--ceph": "wip-leonidc-20240331-00",  # 'main' build not found on shaman
        "--ceph-repo": "https://github.com/ceph/ceph-ci.git",
        "--suite_repo": "https://github.com/ceph/ceph-ci.git",
        "--suite": "teuthology:no-ceph",
        "--machine-type": "testnode",
        "--distro": "ubuntu",
        "--distro-version": "20.04",
        "<config_yaml>": ["/teuthology/containerized_node.yaml"]
    }
    default_args = SuiteArgs(**args).model_dump(by_alias=True)
    default_args["--user"] = get_username(request)
    return run(default_args, logs, access_token)
