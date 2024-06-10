from sqlmodel import Field, SQLModel


class Presets(SQLModel, table=True):
    id: int = Field(primary_key=True)
    username: str = Field(index=True, unique=True)
    name: str = Field(unique=True)
    suite: str
    cmd: str
