import json

import pytest

from src.snipster.exceptions import (
    NoTagsPresent,
    SnippetExists,
    SnippetNotFound,
    TagExists,
    TagNotFound,
)
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


def test_in_memory_toggle_favorite(repo_in_memory):
    assert repo_in_memory.repository["1"]["favorite"] is True
    message = repo_in_memory.toggle_favorite("1")
    assert message == "Snippet ID: 1 favorite updated from True to False"
    assert repo_in_memory.repository["1"]["favorite"] is False


def test_datastore_toggle_favorite(repo_in_datastore, snippet_two):
    repo_in_datastore.add(snippet_two)
    snippet = repo_in_datastore.get(2)
    assert snippet["favorite"] is True

    message = repo_in_datastore.toggle_favorite(2)
    assert message == "Snippet ID: 2 favorite updated from True to False"

    snippet = repo_in_datastore.get(2)
    assert snippet["favorite"] is False


def test_datastore_toggle_favorite_error(repo_in_datastore):
    with pytest.raises(SnippetNotFound):
        repo_in_datastore.toggle_favorite(100)


def test_json_repository_toggle_favorite(temp_json_file, snippet_one, snippet_two):
    snippet_one.id = 10
    snippet_two.id = 20
    with JSONRepository(temp_json_file) as repo:
        repo.add(snippet_one)
        repo.add(snippet_two)
        assert repo.repository["10"]["favorite"] is True
        repo.toggle_favorite("10")
        assert repo.repository["10"]["favorite"] is False


def test_in_memory_add_tag(repo_in_memory):
    message = repo_in_memory.tag("1", "python")
    assert message == "Tags ('python',) were added for Snippet ID: 1"


def test_in_memory_add_tags(repo_in_memory):
    message = repo_in_memory.tag("1", "json", "sql")
    assert message == "Tags ('json', 'sql') were added for Snippet ID: 1"


def test_in_memory_add_tags_error(repo_in_memory):
    with pytest.raises(TagExists):
        repo_in_memory.tag("1", "python")


def test_in_memory_remove_tags(repo_in_memory):
    repo_in_memory.tag("1", "rust", "dry")
    assert len(repo_in_memory.repository["1"]["tags"].split(", ")) == 5
    message = repo_in_memory.tag("1", "json", "python", remove=True)
    assert message == "Tags ('json', 'python') were removed from Snippet ID: 1"
    assert len(repo_in_memory.repository["1"]["tags"].split(", ")) == 3


def test_in_memory_remove_tag_error(repo_in_memory):
    with pytest.raises(TagNotFound):
        repo_in_memory.tag("1", "javascript", remove=True)

    repo_in_memory.tag("1", "sql", "rust", "dry", remove=True)

    with pytest.raises(NoTagsPresent):
        repo_in_memory.tag("1", "python", remove=True)


def test_datastore_add_tag(repo_in_datastore):
    message = repo_in_datastore.tag(1, "python")
    assert message == "Tags ('python',) were added for Snippet ID: 1"


def test_datastore_add_tags(repo_in_datastore):
    message = repo_in_datastore.tag(1, "json", "javascript", "typescript")
    assert (
        message
        == "Tags ('json', 'javascript', 'typescript') were added for Snippet ID: 1"
    )


def test_datastore_add_tags_error(repo_in_datastore):
    with pytest.raises(TagExists):
        repo_in_datastore.tag(1, "python")


def test_datastore_remove_tag(repo_in_datastore):
    message = repo_in_datastore.tag(1, "python", "json", "typescript", remove=True)
    assert (
        message
        == "Tags ('python', 'json', 'typescript') were removed from Snippet ID: 1"
    )


def test_datastore_remove_tag_error(repo_in_datastore):
    with pytest.raises(TagNotFound):
        repo_in_datastore.tag(1, "django", remove=True)

    repo_in_datastore.tag(1, "javascript", remove=True)

    with pytest.raises(NoTagsPresent):
        repo_in_datastore.tag(1, "python", remove=True)
