from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import Session
from schemas.presets import PresetSchema
from . import Base


class Presets(Base):
    __tablename__ = "presets"
    id = Column(Integer, primary_key=True)
    username = Column(String, index=True)
    name = Column(String)
    suite = Column(String)
    cmd = Column(String)

    __table_args__ = (UniqueConstraint("username", "name"),)


class PresetsDatabaseException(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


def create_preset(db: Session, preset: PresetSchema):
    new_preset = Presets(**preset.model_dump())
    db.add(new_preset)
    db.commit()
    db.refresh(new_preset)
    return new_preset


def get_presets_by_username(db: Session, username: str):
    db_preset = db.query(Presets).filter(Presets.username == username).all()
    return db_preset


def get_preset_by_username_name(db: Session, username: str, preset_name: str):
    db_preset = (
        db.query(Presets)
        .filter(Presets.username == username, Presets.name == preset_name)
        .first()
    )
    return db_preset


def get_preset_id(db: Session, preset_id: int):
    db_preset = db.query(Presets).filter(Presets.id == preset_id).first()
    return db_preset


def update_preset(db: Session, preset_id: int, update_data):
    preset_query = db.query(Presets).filter(Presets.id == preset_id)
    db_preset = preset_query.first()
    if not db_preset:
        raise PresetsDatabaseException("Preset does not exist - unable to update.", 404)
    preset_query.filter(Presets.id == preset_id).update(
        update_data, synchronize_session=False
    )
    db.commit()
    db.refresh(db_preset)
    return db_preset


def delete_preset(db: Session, preset_id: int):
    preset_query = db.query(Presets).filter(Presets.id == preset_id)
    db_preset = preset_query.first()
    if not db_preset:
        raise PresetsDatabaseException("Preset does not exist - unable to delete.", 404)
    preset_query.delete(synchronize_session=False)
    db.commit()
