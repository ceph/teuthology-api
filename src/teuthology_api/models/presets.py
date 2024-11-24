from pydantic import ConfigDict
from sqlmodel import Column, Field, JSON, SQLModel, UniqueConstraint


class Presets(SQLModel, table=True):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int = Field(primary_key=True)
    username: str = Field(index=True)
    name: str
    suite: str
    cmd: JSON = Field(sa_column=Column(JSON))

    __table_args__ = (UniqueConstraint("username", "name"),)
