import logging

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks

from teuthology_api.services.suite import run
from teuthology_api.services.helpers import get_token
from teuthology_api.schemas.suite import SuiteArgs

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/suite",
    tags=["suite"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", status_code=200)
async def create_run(
    args: SuiteArgs,
    background_tasks: BackgroundTasks,
    access_token: str = Depends(get_token),
    dry_run: bool = False,
    logs: bool = False,
    background: bool = True,
):
    if background:
        background_tasks.add_task(run, args, dry_run, logs, access_token)
        return {"msg": "Task running in background."}
    
    args = args.model_dump(by_alias=True)
    return run(args, dry_run, logs, access_token)
