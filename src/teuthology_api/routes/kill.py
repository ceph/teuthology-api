import logging

from fastapi import APIRouter, Depends, Request

from teuthology_api.services.kill import run
from teuthology_api.services.helpers import get_token
from teuthology_api.schemas.kill import KillArgs

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/kill",
    tags=["kill"],
)


@router.post("/", status_code=200)
def create_run(
    request: Request,
    args: KillArgs,
    logs: bool = False,
    access_token: str = Depends(get_token),
):
    """
    POST route for killing a run or a job.

    Note: I needed to put `request` before `args`
    or else it will SyntaxError: non-dafault
    argument follows default argument error.
    """
    args = args.model_dump(by_alias=True, exclude_unset=True)
    return run(args, logs, access_token, request)
