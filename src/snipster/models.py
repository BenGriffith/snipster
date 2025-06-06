from datetime import datetime, timezone
from enum import Enum

from decouple import config
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Column, Field, SQLModel, create_engine

DATABASE_URL = config("DATABASE_URL", cast=str)


class Language(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    RUST = "rust"
    GO = "go"
    TYPESCRIPT = "typescript"
    SQL = "sql"
    PLSQL = "plsql"


class Snippet(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    code: str
    description: str | None
    language: Language = Field(sa_column=Column(SQLAlchemyEnum(Language)))
    tags: str | None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    favorite: bool


if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    SQLModel.metadata.create_all(engine)
