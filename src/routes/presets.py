from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
import logging

from services.helpers import get_token
from models import get_db
from services.presets import PresetsDatabaseException, PresetsService
from schemas.presets import PresetsSchema

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/presets",
    tags=["presets"],
)


@router.get("/", status_code=200)
def read_preset(username: str, name: str, db: Session = Depends(get_db)):
    db_preset = PresetsService(db).get_by_username_and_name(username, name)
    if not db_preset:
        raise HTTPException(status_code=404, detail=f"Preset does not exist.")
    return db_preset


@router.get("/list", status_code=200)
def read_preset(username: str, db: Session = Depends(get_db)):
    db_presets = PresetsService(db).get_by_username(username)
    if not db_presets:
        raise HTTPException(status_code=404, detail=f"User has no presets saved.")
    return db_presets


@router.post("/add", status_code=200)
def add_preset(
    preset: PresetsSchema,
    db: Session = Depends(get_db),
    access_token: str = Depends(get_token),
):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="You need to be logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_preset = PresetsService(db).get_by_username_and_name(
        username=preset.username, preset_name=preset.name
    )
    if db_preset:
        raise HTTPException(
            status_code=400, detail=f"Preset of this username & name already exists."
        )
    return PresetsService(db).create(preset.model_dump())


@router.put("/edit/{preset_id}", status_code=200)
def update_preset(
    preset_id: int,
    updated_data: PresetsSchema,
    db: Session = Depends(get_db),
    access_token: str = Depends(get_token),
):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="You need to be logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return PresetsService(db).update(
            preset_id, updated_data.model_dump(exclude_unset=True)
        )
    except PresetsDatabaseException as exc:
        raise HTTPException(
            status_code=exc.code,
            detail=str(exc),
        )


@router.delete("/delete/{preset_id}", status_code=204)
def delete_preset(
    preset_id: int,
    db: Session = Depends(get_db),
    access_token: str = Depends(get_token),
):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="You need to be logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        PresetsService(db).delete(preset_id)
    except PresetsDatabaseException as exc:
        raise HTTPException(
            status_code=exc.code,
            detail=str(exc),
        )
