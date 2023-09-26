from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session
from . import Base


class AutoSuite(Base):
    __tablename__ = 'auto_suite'
    id  = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    status = Column(String)
    created_at = Column(DateTime(timezone=True))
    scheduling_started_at = Column(DateTime(timezone=True))
    branch = Column(String)
    distro = Column(String)
    distro_version = Column(String)
    flavor = Column(String)
    suite = Column(String)
    log_path = Column(String)
    cmd = Column(String)


class AutoSuiteDatabaseException(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


def create_autosuite(db: Session, auto_suite):
    new_autosuite = AutoSuite(**auto_suite)
    db.add(new_autosuite)
    db.commit()
    db.refresh(new_autosuite)
    return new_autosuite


def get_autosuites_by_username(db: Session, username: str):
    db_autosuite = db.query(AutoSuite).filter(AutoSuite.username == username).all()
    return db_autosuite


def update_autosuite(db: Session, record_id: int, update_data):
    autosuite_query = db.query(AutoSuite).filter(AutoSuite.id == record_id)
    db_autosuite = autosuite_query.first()
    if not db_autosuite:
        raise AutoSuiteDatabaseException("AutoSuite object does not exist - unable to update.", 404)
    autosuite_query.filter(AutoSuite.id == record_id).update(
        update_data, synchronize_session=False
    )
    db.commit()
    db.refresh(db_autosuite)
    return db_autosuite