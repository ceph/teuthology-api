import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from models import get_db
from services.auto_suite import AutoSuiteService, auto_schedule
from schemas.auto_suite import AutoSuiteSchema, BuildStatusWebhook

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auto-schedule",
    tags=["auto-schedule"],
)


@router.post("/", status_code=200)
def create_auto_suite(payload: AutoSuiteSchema, db: Session = Depends(get_db)):
    return AutoSuiteService(db).create(payload.model_dump())


@router.get("/", status_code=200)
def get_auto_suite(username: str, db: Session = Depends(get_db)):
    db_record = AutoSuiteService(db).get_by_username(username)
    if not db_record:
        raise HTTPException(
            status_code=404, detail=f"User has no auto_suite scheduled."
        )
    return db_record


@router.post("/webhook/build-status", status_code=201)
def build_status_webhook(
    ready_builds: BuildStatusWebhook, db: Session = Depends(get_db)
):
    db_records = AutoSuiteService(db).get_by_build_data(ready_builds)
    if db_records:
        auto_schedule(db_records)
    return db_records
