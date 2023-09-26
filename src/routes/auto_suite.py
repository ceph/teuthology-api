import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from models import get_db
from schemas.auto_suite import AutoSuiteSchema, BuildStatusWebhookArgs
from models import auto_suite as auto_suite_model

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auto-schedule",
    tags=["auto-schedule"],
)


@router.post("/", status_code=200)
def create_auto_suite(payload: AutoSuiteSchema, db: Session = Depends(get_db)):
    return auto_suite_model.create_autosuite(db, payload.model_dump())


@router.get("/", status_code=200)
def get_auto_suite(username: str, db: Session = Depends(get_db)):
    db_presets = auto_suite_model.get_autosuites_by_username(db, username)
    if not db_presets:
        raise HTTPException(status_code=404, detail=f"User has no auto_suite scheduled.")
    return db_presets


@router.post("/webhook/build-status", status_code=201)
def build_status_webhook(payload: BuildStatusWebhookArgs):
    # TODO: need to implement this
    return payload