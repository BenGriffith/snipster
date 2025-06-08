from typer.testing import CliRunner

from src.snipster.cli import app

runner = CliRunner()


def test_cli_add(repo_in_datastore):
    result = runner.invoke(
        app,
        [
            "add",
            "--title",
            "first_snippet",
            "--code",
            "print('hello world')",
            "--description",
            "first snippet submission",
            "--language",
            "python",
        ],
        obj=repo_in_datastore,
    )
    assert result.exit_code == 0
    assert (
        result.output
        == "Snippet ID: 1 was created and added to the Snippet Repository\n"
    )


def test_cli_add_error(repo_in_datastore):
    result = runner.invoke(
        app,
        [
            "add",
            "--title",
            "second snippet",
            "--code",
            "print('boom goes the dynamite')",
            "--language",
            "coffeescript",
        ],
        obj=repo_in_datastore,
    )
    assert result.exit_code == 2
    assert "Invalid value" in result.output


def test_cli_get(repo_in_datastore):
    result = runner.invoke(app, ["get", "--id", "1"], obj=repo_in_datastore)
    assert result.exit_code == 0
    assert "first_snippet" in result.output
    assert "print('hello world')" in result.output


def test_cli_get_none(repo_in_datastore):
    result = runner.invoke(app, ["get", "--id", 2], obj=repo_in_datastore)
    assert "None" in result.output
