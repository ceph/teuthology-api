from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import Session
from . import Base
from teuthology_api.schemas.presets import PresetsSchema



class Presets(Base):
    __tablename__ = "presets"
    id = Column(Integer, primary_key=True)
    username = Column(String, index=True)
    name = Column(String)
    suite = Column(String)
    cmd = Column(String)

    __table_args__ = (UniqueConstraint("username", "name"),)


def create_preset(db: Session, preset: PresetsSchema):
    new_preset = Presets(**preset.model_dump())
    db.add(new_preset)
    db.commit()
    db.refresh(new_preset)
    return new_preset


def get_user_presets(db: Session, username: str):
    return db.query(Presets).filter(Presets.username == username).all()


def get_preset(db: Session, username: str, preset_name: str):
    return (
        db.query(Presets)
        .filter(Presets.username == username, Presets.name == preset_name)
        .first()
    )
