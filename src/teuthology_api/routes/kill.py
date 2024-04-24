import logging

from fastapi import APIRouter, Depends, Request, HTTPException
from requests.exceptions import HTTPError

from teuthology_api.services.kill import run
from teuthology_api.services.helpers import get_token
from teuthology_api.schemas.kill import KillArgs

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/kill",
    tags=["kill"],
)


@router.post("/", status_code=200)
async def create_run(
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
    try:
        args = args.model_dump(by_alias=True, exclude_unset=True)
        return await run(args, logs, access_token, request)
    except HTTPException:
        raise
    except HTTPError as http_err:
        log.error(http_err)
        raise HTTPException(
            status_code=http_err.response.status_code, detail=repr(http_err)
        ) from http_err
    except Exception as err:
        log.error(err)
        raise HTTPException(status_code=500, detail=repr(err)) from err
