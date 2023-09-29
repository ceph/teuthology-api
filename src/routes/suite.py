from fastapi import APIRouter, HTTPException, Depends
from services.suite import run
from services.helpers import get_token
from schemas.suite import SuiteArgs
import logging

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/suite",
    tags=["suite"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", status_code=200)
def create_run(
    args: SuiteArgs,
    access_token: str = Depends(get_token),
    dry_run: bool = False,
    logs: bool = False,
):
    args = args.model_dump(by_alias=True)
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="You need to be logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return run(args, dry_run, logs)
