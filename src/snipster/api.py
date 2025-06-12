from fastapi import Depends, FastAPI, Query
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


@app.get("/snippets/", response_model=list[SnippetPublic], status_code=200)
def get_snippets(repo: Session = Depends(get_repo)):
    snippets = repo.all()
    return snippets


@app.get("/snippets/{snippet_id}", response_model=SnippetPublic, status_code=200)
def get_snippet(snippet_id: int, repo: Session = Depends(get_repo)):
    snippet = repo.get(snippet_id)
    return snippet


@app.delete("/snippets/{snippet_id}")
def delete_snippet(snippet_id: int, repo: Session = Depends(get_repo)):
    result = repo.delete(snippet_id)
    return {"message": result}


@app.post("/snippets/{snippet_id}/favorite", response_model=dict)
def toggle_favorite(snippet_id: int, repo: Session = Depends(get_repo)):
    result = repo.toggle_favorite(snippet_id)
    return {"message": result}


@app.post("/snippets/{snippet_id}/tags", response_model=dict)
def update_tags(
    snippet_id: int,
    tags: list[str] = Query(...),
    remove: bool = False,
    repo: Session = Depends(get_repo),
):
    result = repo.tag(snippet_id, ", ".join(tags), remove=remove)
    return {"message": result}
