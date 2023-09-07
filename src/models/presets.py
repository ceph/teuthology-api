from sqlalchemy import Column, Integer, String, UniqueConstraint
from . import Base

class Presets(Base):
    __tablename__ = 'presets'
    id  = Column(Integer, primary_key=True)
    username = Column(String, index=True)
    name = Column(String)
    suite = Column(String)
    cmd = Column(String)

    __table_args__ = (
        UniqueConstraint("username", "name"),
    )
