from sqlalchemy.orm import Session
from teuthology_api.models.presets import Presets


class PresetsDatabaseException(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


class PresetsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_username(self, username: str):
        db_preset = self.db.query(Presets).filter(Presets.username == username).all()
        return db_preset

    def get_by_username_and_name(self, username: str, preset_name: str):
        db_preset = (
            self.db.query(Presets)
            .filter(Presets.username == username, Presets.name == preset_name)
            .first()
        )
        return db_preset

    def get_by_id(self, preset_id: int):
        db_preset = self.db.query(Presets).filter(Presets.id == preset_id).first()
        return db_preset

    def create(self, preset: dict) -> Presets:
        new_preset = Presets(**preset)
        self.db.add(new_preset)
        self.db.commit()
        self.db.refresh(new_preset)
        return new_preset

    def update(self, preset_id: int, update_data):
        preset_query = self.db.query(Presets).filter(Presets.id == preset_id)
        db_preset = preset_query.first()
        if not db_preset:
            raise PresetsDatabaseException(
                "Presets does not exist - unable to update.", 404
            )
        preset_query.filter(Presets.id == preset_id).update(
            update_data, synchronize_session=False
        )
        self.db.commit()
        self.db.refresh(db_preset)
        return db_preset

    def delete(self, preset_id: int):
        preset_query = self.db.query(Presets).filter(Presets.id == preset_id)
        db_preset = preset_query.first()
        if not db_preset:
            raise PresetsDatabaseException(
                "Presets does not exist - unable to delete.", 404
            )
        preset_query.delete(synchronize_session=False)
        self.db.commit()
