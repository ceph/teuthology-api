from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session
from . import Base


class AutoSuite(Base):
    __tablename__ = "auto_suite"
    id = Column(Integer, primary_key=True, index=True)
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
