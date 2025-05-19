import pytest
from sqlmodel import Session, SQLModel, create_engine


@pytest.fixture
def test_engine():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(test_engine):
    with Session(test_engine) as session:
        yield session
