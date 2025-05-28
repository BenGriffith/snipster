import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.snipster.models import Language, Snippet
from src.snipster.repo import DatastoreRepository, InMemoryRepository


@pytest.fixture(scope="module")
def test_engine():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


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
        favorite=False,
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
