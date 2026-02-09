import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Header, Request

from teuthology_api.services.suite import run
from teuthology_api.services.helpers import resolve_access_token
from teuthology_api.schemas.suite import SuiteArgs

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/suite",
    tags=["suite"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", status_code=200)
async def create_run(
    request: Request,
    args: SuiteArgs,
    logs: bool = False,
    access_token: Optional[str] = Header(
        default=None,
        alias="X-Access-Token",
        description="GitHub access token for headless auth (alternative to Authorization header)",
    ),
):
    """
    Schedule a teuthology suite run.

    Authentication options (in order of precedence):
    1. Authorization: Bearer <token> header (or X-Access-Token header)
    2. Session cookie - browser-based login

    For headless/CI usage, obtain a token via the device flow:
    - POST /login/device/code -> get user_code and verification_uri
    - User visits verification_uri and enters user_code
    - POST /login/device/token -> poll until access_token is returned
    - Use the access_token in X-Access-Token header or Authorization: Bearer header
    """
    # Resolve token and username from various auth sources (never use body for --user)
    username, token_dict = await resolve_access_token(request, access_token)

    args = args.model_dump(by_alias=True)
    # Force both from auth: --user => run name + subprocess USER; --owner => scheduler ownership (kill permission)
    args["--user"] = username
    args["--owner"] = username
    log.info("Scheduling suite as user: %s", username)
    try:
        created_run = run(args, logs, token_dict)
        log.debug(created_run)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return created_run

