import typer
from sqlmodel import Session

from snipster.models import DATABASE_URL, Language, Snippet, create_engine
from snipster.repo import DatastoreRepository

app = typer.Typer()


@app.callback()
def init(ctx: typer.Context):
    if ctx.obj is None:
        engine = create_engine(DATABASE_URL)
        ctx.obj = DatastoreRepository(Session(engine))


@app.command()
def add(
    ctx: typer.Context,
    title: str = typer.Option(..., help="Snippet title"),
    code: str = typer.Option(..., help="Code snippet"),
    description: str = typer.Option(
        None, help="Verbose summary or notes about the snippet"
    ),
    language: str = typer.Option(..., help="Programming language used"),
    tags: str = typer.Option(
        None, help="Short, descriptive label used to group snippets"
    ),
    favorite: bool = typer.Option(False, help="Mark this snippet as a favorite"),
):
    languages = [language.value for language in Language]
    if language.lower() not in languages:
        raise typer.BadParameter(f"Language must be {', '.join(languages)}")
    language = Language(language)
    repo: DatastoreRepository = ctx.obj
    snippet = Snippet(
        title=title,
        code=code,
        description=description,
        language=language,
        tags=tags,
        favorite=favorite,
    )
    snippet = repo.add(snippet)
    print(snippet)


@app.command()
def all(ctx: typer.Context):
    repo: DatastoreRepository = ctx.obj
    snippets = repo.all()
    print(snippets)


@app.command()
def get(ctx: typer.Context, id: int = typer.Option(..., help="Snippet ID to fetch")):
    repo: DatastoreRepository = ctx.obj
    snippet = repo.get(id)
    print(snippet)


@app.command()
def delete(
    ctx: typer.Context, id: int = typer.Option(..., help="Snippet ID to delete")
):
    repo: DatastoreRepository = ctx.obj
    snippet = repo.delete(id)
    print(snippet)


@app.command()
def favorite(
    ctx: typer.Context,
    id: int = typer.Option(..., help="Snippet ID to mark or unmark as favorite"),
):
    repo: DatastoreRepository = ctx.obj
    snippet = repo.toggle_favorite(id)
    print(snippet)


@app.command()
def tag(
    ctx: typer.Context,
    id: int = typer.Option(..., help="Snippet ID to assign tag(s)"),
    tags: str = typer.Option(..., help="Comma-separated list of tags"),
    remove: bool = typer.Option(
        False, help="Set to true if you would like to remove the tag"
    ),
):
    repo: DatastoreRepository = ctx.obj
    snippet = repo.tag(id, tags, remove=remove)
    print(snippet)
