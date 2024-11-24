import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session

from teuthology_api.models.presets import Presets

load_dotenv()

DATABASE_URL = os.getenv("TEUTHOLOGY_API_SQLITE_URI")

engine = create_engine(DATABASE_URL)


def get_db():
    with Session(engine) as session:
        yield session
