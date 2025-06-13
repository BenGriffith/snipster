from snipster.models import Language, Snippet


def test_snippet(session):
    snippet = Snippet(
        title="first snippet",
        code="print('Hello World')",
        description="code snippet for testing purposes",
        language=Language.PYTHON,
        favorite=False,
    )
    session.add(snippet)
    session.commit()
    session.refresh(snippet)

    assert snippet.id is not None
    assert snippet.title == "first snippet"
    assert snippet.language.value == "python"
    assert snippet.created_at is not None
    assert snippet.updated_at is not None
