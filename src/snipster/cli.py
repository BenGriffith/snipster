import typer
from sqlmodel import Session

from src.snipster.models import DATABASE_URL, Language, Snippet, create_engine
from src.snipster.repo import DatastoreRepository

app = typer.Typer()


@app.callback()
def init(ctx: typer.Context):
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
    repo.add(snippet)


@app.command()
def all():
    pass


@app.command()
def get():
    pass


@app.command()
def delete():
    pass


@app.command()
def toggle_favorite():
    pass


@app.command()
def tag():
    pass
