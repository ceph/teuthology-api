from typing import Union

from sqlmodel import select, Session

from teuthology_api.models.presets import Presets


class PresetsDatabaseException(Exception):
    def __init__(self, message: str, code: int) -> None:
        super().__init__(message)
        self.code = code


class PresetsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_username(self, username: str):
        statement = (
            select(Presets).where(Presets.username == username).order_by(Presets.id)
        )
        db_presets = self.db.exec(statement).all()
        return db_presets

    def get_by_username_and_name(
        self, username: str, preset_name: str
    ) -> Union[Presets, None]:
        statement = select(Presets).where(
            Presets.username == username, Presets.name == preset_name
        )
        db_preset = self.db.exec(statement).first()
        return db_preset

    def get_by_id(self, preset_id: int) -> Union[Presets, None]:
        statement = select(Presets).where(Presets.id == preset_id)
        db_preset = self.db.exec(statement).first()
        return db_preset

    def create(self, preset: Presets) -> Presets:
        self.db.add(preset)
        self.db.commit()
        self.db.refresh(preset)
        return preset

    def update(self, preset_id: int, updated_data: dict) -> Presets:
        db_preset = self.get_by_id(preset_id)
        if db_preset is None:
            raise PresetsDatabaseException(
                "Preset does not exist, unable to update", 404
            )

        db_preset.sqlmodel_update(updated_data)
        return self.create(db_preset)

    def delete(self, preset_id: int) -> None:
        db_preset = self.get_by_id(preset_id)
        if db_preset is None:
            raise PresetsDatabaseException(
                "Preset does not exist, unable to delete", 404
            )

        self.db.delete(db_preset)
        self.db.commit()
