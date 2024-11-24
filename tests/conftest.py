"""
    Dummy conftest.py for teuthology_api.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    - https://docs.pytest.org/en/stable/fixture.html
    - https://docs.pytest.org/en/stable/writing_plugins.html
"""

import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from teuthology_api.main import app
from teuthology_api.models import get_db
from teuthology_api.services.helpers import get_token


def override_get_token():
    return {"access_token": "token_123", "token_type": "bearer"}


@pytest.fixture(name="session", scope="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client", scope="session")
def client_fixture(session: Session):
    def override_get_db():
        return session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_token] = override_get_token

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
