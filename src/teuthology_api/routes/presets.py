import logging

from fastapi import status, APIRouter, HTTPException, Depends
from sqlmodel import Session

from teuthology_api.services.helpers import get_token
from teuthology_api.models import get_db, Presets
from teuthology_api.services.presets import PresetsDatabaseException, PresetsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/presets", tags=["presets"])


@router.get("/", status_code=status.HTTP_200_OK)
def read_preset(username: str, name: str, db: Session = Depends(get_db)):
    db_preset = PresetsService(db).get_by_username_and_name(username, name)
    if db_preset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{name} preset does not exist.",
        )
    return db_preset


@router.get("/list", status_code=status.HTTP_200_OK)
def read_all_presets(username: str, db: Session = Depends(get_db)):
    db_presets = PresetsService(db).get_by_username(username)
    if not db_presets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User has not presets saved.",
        )
    return db_presets


@router.post("/add", status_code=status.HTTP_201_CREATED)
def add_preset(
    preset: Presets,
    db: Session = Depends(get_db),
    access_token: str = Depends(get_token),
):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You need to be logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_preset_exists = PresetsService(db).get_by_username_and_name(
        preset.username, preset.name
    )
    if db_preset_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Preset with name {preset.name} exists",
        )
    return PresetsService(db).create(preset)


@router.put("/edit/{preset_id}", status_code=status.HTTP_200_OK)
def update_preset(
    preset_id: int,
    updated_preset: Presets,
    db: Session = Depends(get_db),
    access_token: str = Depends(get_token),
):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You need to be logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return PresetsService(db).update(
            preset_id, updated_preset.model_dump(exclude_unset=True)
        )
    except PresetsDatabaseException as exc:
        raise HTTPException(status_code=exc.code, detail=str(exc))


@router.delete("/delete/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_preset(
    preset_id: int,
    db: Session = Depends(get_db),
    access_token: str = Depends(get_token),
):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You need to be logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        PresetsService(db).delete(preset_id)
    except PresetsDatabaseException as exc:
        raise HTTPException(status_code=exc.code, detail=str(exc))
