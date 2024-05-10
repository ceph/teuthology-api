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
    try:
        created_run = run(args, logs, access_token)
        log.debug(created_run)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return created_run
