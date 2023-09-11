from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
import logging

from services.helpers import get_token
from models import get_db
from models.presets import PresetsDatabaseException
from models import presets as presets_model
from schemas.presets import PresetSchema

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/presets",
    tags=["presets"],
)


@router.get("/", status_code=200)
def read_preset(username: str, name: str, db: Session = Depends(get_db)):
    db_preset = presets_model.get_preset_by_username_name(db, username, name)
    if not db_preset:
        raise HTTPException(status_code=404, detail=f"Preset does not exist.")
    return db_preset


@router.get("/list", status_code=200)
def read_preset(username: str, db: Session = Depends(get_db)):
    db_presets = presets_model.get_presets_by_username(db, username)
    if not db_presets:
        raise HTTPException(status_code=404, detail=f"User has no presets saved.")
    return db_presets


@router.post("/add", status_code=200)
def add_preset(
    preset: PresetSchema,
    db: Session = Depends(get_db),
    access_token: str = Depends(get_token),
):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="You need to be logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_preset = presets_model.get_preset_by_username_name(
        db, username=preset.username, preset_name=preset.name
    )
    if db_preset:
        raise HTTPException(
            status_code=400, detail=f"Preset of this username & name already exists."
        )
    return presets_model.create_preset(db, preset.model_dump())


@router.put("/edit/{preset_id}", status_code=200)
def update_preset(
    preset_id: int,
    updated_data: PresetSchema,
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
        return presets_model.update_preset(
            db, preset_id, updated_data.model_dump(exclude_unset=True)
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
        presets_model.delete_preset(db, preset_id)
    except PresetsDatabaseException as exc:
        raise HTTPException(
            status_code=exc.code,
            detail=str(exc),
        )
