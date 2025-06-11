from fastapi import Depends, FastAPI
from sqlmodel import Session

from snipster.models import Language, Snippet, SnippetCreate, SnippetPublic, get_session
from snipster.repo import DatastoreRepository


def get_repo():
    session_gen = get_session()
    session = next(session_gen)
    try:
        yield DatastoreRepository(session)
    finally:
        session_gen.close()


app = FastAPI()


@app.post("/snippets/", response_model=SnippetPublic, status_code=201)
def create_snippet(snippet: SnippetCreate, repo: Session = Depends(get_repo)):
    db_snippet = Snippet(
        title=snippet.title,
        code=snippet.code,
        description=snippet.description,
        language=Language(snippet.language),
        tags=snippet.tags,
        favorite=snippet.favorite,
    )
    repo.add(db_snippet)
    return db_snippet.model_dump()
