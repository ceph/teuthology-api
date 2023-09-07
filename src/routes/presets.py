from fastapi import APIRouter, HTTPException, Depends
from models import get_db
from models.presets import get_preset, get_user_presets, create_preset
from schemas.presets import PresetSchema
from sqlalchemy.orm import Session
import logging

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/presets",
    tags=["presets"],
)


@router.get("/", status_code=200)
def read_preset(username: str, name: str, db: Session = Depends(get_db)):
    db_preset = get_preset(db, username, name)
    return db_preset


@router.get("/list", status_code=200)
def read_preset(username: str, db: Session = Depends(get_db)):
    db_presets = get_user_presets(db, username)
    return db_presets


@router.post("/add", status_code=200, response_model=PresetSchema)
def add_preset(preset: PresetSchema, db: Session = Depends(get_db)):
    db_preset = get_preset(db, username=preset.username, preset_name=preset.name)
    if db_preset:
        raise HTTPException(
            status_code=400, detail=f"Preset '{preset.name}' already exists."
        )
    return create_preset(db, preset)
