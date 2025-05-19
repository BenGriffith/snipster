import pytest
from sqlmodel import Session, SQLModel, create_engine


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def session(test_engine):
    with Session(test_engine) as session:
        yield session
