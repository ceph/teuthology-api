from sqlmodel import Field, SQLModel, UniqueConstraint


class Presets(SQLModel, table=True):
    id: int = Field(primary_key=True)
    username: str = Field(index=True)
    name: str
    suite: str
    cmd: str

    __table_args__ = (UniqueConstraint("username", "name"),)
