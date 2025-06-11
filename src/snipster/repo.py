import json
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

from sqlmodel import select

from snipster.exceptions import (
    NoTagsPresent,
    SnippetExists,
    SnippetNotFound,
    TagExists,
    TagNotFound,
)
from snipster.models import Snippet


class SnippetRepository(ABC):
    @abstractmethod
    def add(self, snippet):
        pass

    @abstractmethod
    def all(self):
        pass

    @abstractmethod
    def get(self, snippet_id):
        pass

    @abstractmethod
    def delete(self, snippet_id):
        pass

    @abstractmethod
    def toggle_favorite(self, snippet_id):
        pass

    @abstractmethod
    def tag(self, snippet_id, *tags, remove=False):
        existing_tags = self._existing_tag(snippet_id)
        if remove:
            return self._remove_tag(snippet_id, *tags, existing_tags=existing_tags)
        return self._add_tag(snippet_id, *tags, existing_tags=existing_tags)

    @abstractmethod
    def _existing_tag(self, snippet_id):
        pass

    @abstractmethod
    def _save_tag(self, snippet_id, updated):
        pass

    @abstractmethod
    def _add_tag(self, snippet_id, *tags, existing_tags):
        conflict = [tag for tag in tags if tag in existing_tags]
        if conflict:
            raise TagExists(snippet_id, conflict)
        updated = existing_tags + list(tags)
        self._save_tag(snippet_id, updated)
        return f"Tags {tags} were added for Snippet ID: {snippet_id}"

    @abstractmethod
    def _remove_tag(self, snippet_id, *tags, existing_tags):
        if not existing_tags:
            raise NoTagsPresent(snippet_id)

        missing = [tag for tag in tags if tag not in existing_tags]
        if missing:
            raise TagNotFound(snippet_id, missing)

        updated = [tag for tag in existing_tags if tag not in tags]
        self._save_tag(snippet_id, updated)
        return f"Tags {tags} were removed from Snippet ID: {snippet_id}"


class InMemoryRepository(SnippetRepository):
    def __init__(self):
        self.repository = {}

    def add(self, snippet):
        snippet = snippet.model_dump()
        id = str(snippet["id"])
        if id in self.repository:
            raise SnippetExists(id)
        self.repository[id] = snippet
        return f"Snippet ID: {id} was created and added to the Snippet Repository"

    def all(self):
        return [{key: value} for key, value in self.repository.items()]

    def get(self, snippet_id):
        if snippet_id in self.repository:
            return self.repository[snippet_id]
        return None

    def delete(self, snippet_id):
        if snippet_id in self.repository:
            del self.repository[snippet_id]
            return f"Snippet ID: {snippet_id} was deleted and removed from the Snippet Repository"
        raise SnippetNotFound(snippet_id)

    def toggle_favorite(self, snippet_id):
        _favorite = self.repository[snippet_id]["favorite"]
        self.repository[snippet_id]["favorite"] = not _favorite
        return f"Snippet ID: {snippet_id} favorite updated from {_favorite} to {self.repository[snippet_id]['favorite']}"

    def tag(self, snippet_id, *tags, remove=False):
        base_result = super().tag(snippet_id, *tags, remove=remove)
        return f"{base_result}"

    def _existing_tag(self, snippet_id):
        existing = self.repository[snippet_id].get("tags", "")
        existing_tags = existing.split(", ") if existing else []
        return existing_tags

    def _save_tag(self, snippet_id, updated):
        self.repository[snippet_id]["tags"] = ", ".join(updated)

    def _add_tag(self, snippet_id, *tags, existing_tags):
        base_result = super()._add_tag(snippet_id, *tags, existing_tags=existing_tags)
        return f"{base_result}"

    def _remove_tag(self, snippet_id, *tags, existing_tags):
        base_result = super()._remove_tag(
            snippet_id, *tags, existing_tags=existing_tags
        )
        return f"{base_result}"


class DatastoreRepository(SnippetRepository):
    def __init__(self, session):
        self.session = session

    def add(self, snippet):
        result = self.get(snippet.id)
        if result is not None:
            raise SnippetExists(snippet.id)

        self.session.add(snippet)
        self.session.commit()
        self.session.refresh(snippet)
        return (
            f"Snippet ID: {snippet.id} was created and added to the Snippet Repository"
        )

    def all(self):
        query = select(Snippet)
        result = self.session.exec(query).all()
        if result:
            result = [row.model_dump() for row in result]
            return result

    def get(self, snippet_id):
        query = select(Snippet).where(Snippet.id == snippet_id)
        result = self.session.exec(query).first()
        if result:
            return result.model_dump()

    def delete(self, snippet_id):
        query = select(Snippet).where(Snippet.id == snippet_id)
        result = self.session.exec(query).first()
        if result:
            id = result.id
            self.session.delete(result)
            self.session.commit()
            return (
                f"Snippet ID: {id} was deleted and removed from the Snippet Repository"
            )
        raise SnippetNotFound(snippet_id)

    def toggle_favorite(self, snippet_id):
        query = select(Snippet).where(Snippet.id == snippet_id)
        result = self.session.exec(query).first()
        if result:
            _favorite = result.favorite
            result.favorite = not result.favorite
            self.session.add(result)
            self.session.commit()
            self.session.refresh(result)
            return f"Snippet ID: {result.id} favorite updated from {_favorite} to {result.favorite}"
        raise SnippetNotFound(snippet_id)

    def tag(self, snippet_id, *tags, remove=False):
        base_result = super().tag(snippet_id, *tags, remove=remove)
        return f"{base_result}"

    def _existing_tag(self, snippet_id, *tags, remove=False):
        query = select(Snippet).where(Snippet.id == snippet_id)
        result = self.session.exec(query).first()
        existing_tags = result.tags.split(", ") if result.tags else []
        return existing_tags

    def _save_tag(self, snippet_id, updated):
        query = select(Snippet).where(Snippet.id == snippet_id)
        result = self.session.exec(query).first()
        result.tags = ", ".join(updated)

        self.session.add(result)
        self.session.commit()
        self.session.refresh(result)

    def _add_tag(self, snippet_id, *tags, existing_tags):
        base_result = super()._add_tag(snippet_id, *tags, existing_tags=existing_tags)
        return f"{base_result}"

    def _remove_tag(self, snippet_id, *tags, existing_tags):
        base_result = super()._remove_tag(
            snippet_id, *tags, existing_tags=existing_tags
        )
        return f"{base_result}"


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class JSONRepository(InMemoryRepository):
    def __init__(self, file):
        super().__init__()
        self.file = file

    def __enter__(self):
        with open(self.file) as file:
            self.repository = json.load(file)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        with open(self.file, "w") as file:
            json.dump(self.repository, file, cls=CustomEncoder)
