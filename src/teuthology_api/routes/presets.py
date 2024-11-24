import logging
from typing import Optional

from fastapi import status, APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from teuthology_api.models import get_db, Presets
from teuthology_api.schemas.preset import PresetArgs, PresetUpdateArgs
from teuthology_api.services.helpers import get_token, get_username
from teuthology_api.services.presets import PresetsDatabaseException, PresetsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/presets", tags=["presets"])


@router.get("/", status_code=status.HTTP_200_OK)
def read_preset(username: str, name: str, db: Session = Depends(get_db)):
    # GitHub usernames are case-insensitive
    username = username.lower()
    db_preset = PresetsService(db).get_by_username_and_name(username, name)
    if db_preset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{name} preset does not exist.",
        )
    return db_preset


@router.get("/list", status_code=status.HTTP_200_OK)
def read_all_presets(
    username: str, suite: Optional[str] = None, db: Session = Depends(get_db)
):
    username = username.lower()
    if suite:
        db_presets = PresetsService(db).get_by_username_and_suite(username, suite)
    else:
        db_presets = PresetsService(db).get_by_username(username)
    if not db_presets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User has not presets saved.",
        )
    return db_presets


@router.post("/add", status_code=status.HTTP_201_CREATED)
def add_preset(
    request: Request,
    preset: PresetArgs,
    replace: bool = False,
    db: Session = Depends(get_db),
    access_token: str = Depends(get_token),
):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You need to be logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = get_username(request).lower()
    db_presets = PresetsService(db).get_by_username(username)
    if len(db_presets) == 10:
        if not replace:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only 10 presets for a user can be stored at a time.",
            )
        # If replace parameter is set true, delete the
        # oldest preset of the user and create a new one
        PresetsService(db).delete(db_presets[0].id)

    db_preset_exists = PresetsService(db).get_by_username_and_name(
        username, preset.name
    )
    if db_preset_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Preset with name {preset.name} exists",
        )

    db_preset = Presets(
        **preset.model_dump(), username=username, suite=preset.cmd["--suite"]
    )
    return PresetsService(db).create(db_preset)


@router.put("/edit/{preset_id}", status_code=status.HTTP_200_OK)
def update_preset(
    preset_id: int,
    preset: PresetUpdateArgs,
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
        updated_preset = preset.model_dump(exclude_unset=True)
        if updated_preset == {}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nothing new to update",
            )
        if preset.cmd:
            updated_preset["suite"] = preset.cmd["--suite"]
        return PresetsService(db).update(preset_id, updated_preset)
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
