import json

import pytest

from src.snipster.exceptions import SnippetExists, SnippetNotFound
from src.snipster.repo import JSONRepository


def test_in_memory_add(repo_in_memory, snippet_one):
    snippet_one.id = 1
    result = repo_in_memory.add(snippet_one)
    assert result == "Snippet ID: 1 was created and added to the Snippet Repository"
    assert repo_in_memory.repository["1"]["title"] == "first snippet"


def test_in_memory_add_error(repo_in_memory, snippet_one):
    snippet_one.id = 1
    with pytest.raises(SnippetExists):
        repo_in_memory.add(snippet_one)


def test_in_memory_all(repo_in_memory, snippet_two):
    snippet_two.id = 2
    repo_in_memory.add(snippet_two)
    all_snippets = repo_in_memory.all()
    assert len(all_snippets) == 2


def test_in_memory_get(repo_in_memory):
    snippet_one = repo_in_memory.get("1")
    snippet_two = repo_in_memory.get("2")
    assert snippet_one["title"] == "first snippet"
    assert snippet_two["title"] == "second snippet"


def test_in_memory_delete(repo_in_memory):
    result = repo_in_memory.delete("2")
    assert result == "Snippet ID: 2 was deleted and removed from the Snippet Repository"
    assert len(repo_in_memory.all()) == 1


def test_in_memory_delete_error(repo_in_memory):
    with pytest.raises(SnippetNotFound):
        repo_in_memory.delete("10")


def test_datastore_add(repo_in_datastore, snippet_one):
    result = repo_in_datastore.add(snippet_one)
    assert result == "Snippet ID: 1 was created and added to the Snippet Repository"


def test_datastore_add_error(repo_in_datastore, snippet_one):
    snippet_one.id = 1
    with pytest.raises(SnippetExists):
        repo_in_datastore.add(snippet_one)


def test_datastore_get_all(repo_in_datastore, snippet_two):
    repo_in_datastore.add(snippet_two)
    result = repo_in_datastore.all()
    assert len(result) == 2


def test_datastore_get(repo_in_datastore):
    result = repo_in_datastore.get(1)
    assert result["title"] == "first snippet"
    assert result["code"] == "print('hello world')"


def test_datastore_delete(repo_in_datastore):
    result = repo_in_datastore.delete(2)
    assert result == "Snippet ID: 2 was deleted and removed from the Snippet Repository"


def test_datastore_delete_error(repo_in_datastore):
    with pytest.raises(SnippetNotFound):
        repo_in_datastore.delete(100)


def test_json_repository_add(temp_json_file, snippet_one, snippet_two):
    snippet_one.id = 1
    snippet_two.id = 2
    with JSONRepository(temp_json_file) as repo:
        assert (
            repo.add(snippet_one)
            == "Snippet ID: 1 was created and added to the Snippet Repository"
        )
        assert (
            repo.add(snippet_two)
            == "Snippet ID: 2 was created and added to the Snippet Repository"
        )

    with open(temp_json_file) as file:
        final = json.load(file)
        assert len(final) == 2


def test_json_repository_delete(temp_json_file, snippet_one, snippet_two):
    snippet_one.id = 10
    snippet_two.id = 20
    with JSONRepository(temp_json_file) as repo:
        repo.add(snippet_one)
        repo.add(snippet_two)

    with JSONRepository(temp_json_file) as repo:
        assert (
            repo.delete("10")
            == "Snippet ID: 10 was deleted and removed from the Snippet Repository"
        )

    with open(temp_json_file) as file:
        final = json.load(file)
        assert len(final) == 1
