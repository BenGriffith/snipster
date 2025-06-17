import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from snipster.api import app, get_repo
from snipster.models import Language, Snippet
from snipster.repo import DatastoreRepository, InMemoryRepository


@pytest.fixture(scope="function")
def test_engine(tmp_path):
    db_file = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_file}", connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    yield engine


@pytest.fixture(scope="function")
def session(test_engine):
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="session")
def repo_in_memory():
    return InMemoryRepository()


@pytest.fixture(scope="function")
def snippet_one():
    snippet = Snippet(
        title="first snippet",
        code="print('hello world')",
        description=None,
        language=Language.PYTHON,
        tags=None,
        favorite=True,
    )
    return snippet


@pytest.fixture(scope="function")
def snippet_two():
    snippet = Snippet(
        title="second snippet",
        code="print('french bulldogs are awesome')",
        description=None,
        language=Language.PYTHON,
        tags=None,
        favorite=True,
    )
    return snippet


@pytest.fixture()
def repo_in_datastore(session):
    return DatastoreRepository(session)


@pytest.fixture()
def temp_json_file(tmp_path):
    file_path = tmp_path / "test.json"
    file_path.write_text("{}")
    return file_path


@pytest.fixture()
def fastapi_client(session):
    def override_repo():
        return DatastoreRepository(session)

    app.dependency_overrides[get_repo] = override_repo
    client = TestClient(app)
    return client
