import logging
from fastapi import APIRouter, Depends, Request
from services.kill import run
from services.helpers import get_token
from schemas.kill import KillArgs

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/kill",
    tags=["kill"],
)


@router.post(
    "/",
    status_code=200,
    responses={
        200: {
            "description": "Run killed successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "log": {
                                "type": "array",
                                "description": "List of logs while executing teuthology-kill",
                                "items": {"type": "string"},
                            },
                            "kill": {
                                "type": "array",
                                "description": "Teuthology-kill executed successfully",
                                "items": {"type": "string"},
                            },
                        },
                        "example": '{"kill": "success"}',
                    }
                }
            },
        },
        400: {
            "description": "Missing argument(s) in request body",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "string",
                        "example": "--run is a required argument",
                    }
                }
            },
        },
        401: {
            "description": "Authorization error: Either user is not logged in or doesn't have the permission to kill the run",
            "content": {
                "application/json": {
                    "schema": {"type": "string", "example": "You need to be logged in"}
                }
            },
        },
        500: {
            "description": "Error while executing teuthology command",
            "content": {"application/json": {"schema": {"type": "string"}}},
        },
    },
)
def create_run(
    request: Request,
    args: KillArgs,
    logs: bool = False,
    access_token: str = Depends(get_token),
):
    """
    Endpoint for killing a run or a job.

    Requires user's GitHub `access_token` for authorization.
    """
    args = args.model_dump(by_alias=True)
    return run(args, logs, access_token, request)
