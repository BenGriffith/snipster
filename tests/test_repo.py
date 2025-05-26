import pytest

from src.snipster.exceptions import SnippetExists, SnippetNotFound


def test_in_memory_add(repo_in_memory, snippet_one):
    result = repo_in_memory.add(snippet_one)
    assert result == "Snippet ID: 1 was created and added to the Snippet Repository"
    assert repo_in_memory.repository["1"]["title"] == "first snippet"


def test_in_memory_add_error(repo_in_memory, snippet_one):
    with pytest.raises(SnippetExists):
        repo_in_memory.add(snippet_one)


def test_in_memory_all(repo_in_memory, snippet_two):
    repo_in_memory.add(snippet_two)
    all_snippets = repo_in_memory.all()
    assert len(all_snippets) == 2


def test_in_memory_get(repo_in_memory):
    snippet_one = repo_in_memory.get("1")
    snippet_two = repo_in_memory.get("2")
    assert snippet_one["title"] == "first snippet"
    assert snippet_two["title"] == "second snippet"


def test_in_memory_get_error(repo_in_memory):
    with pytest.raises(SnippetNotFound):
        repo_in_memory.get("10")


def test_in_memory_delete(repo_in_memory):
    result = repo_in_memory.delete("2")
    assert result == "Snippet ID: 2 was deleted and removed from the Snippet Repository"
    assert len(repo_in_memory.all()) == 1


def test_in_memory_delete_error(repo_in_memory):
    with pytest.raises(SnippetNotFound):
        repo_in_memory.delete("10")
