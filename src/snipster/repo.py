import json
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

from sqlmodel import select

from src.snipster.exceptions import (
    NoTagsPresent,
    SnippetExists,
    SnippetNotFound,
    TagExists,
    TagNotFound,
)
from src.snipster.models import Snippet


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
        pass

    @abstractmethod
    def _add_tag(self, snippet_id, *tags, existing_tags):
        pass

    @abstractmethod
    def _remove_tag(self, snippet_id, *tags, existing_tags):
        pass


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
        existing = self.repository[snippet_id].get("tags", "")
        existing_tags = existing.split(", ") if existing else []

        if remove:
            return self._remove_tag(snippet_id, *tags, existing_tags)
        return self._add_tag(snippet_id, *tags, existing_tags)

    def _add_tag(self, snippet_id, *tags, existing_tags):
        conflict = [tag for tag in tags if tag in existing_tags]
        if conflict:
            raise TagExists(snippet_id, conflict)
        updated = existing_tags + list(*tags)
        self.repository[snippet_id]["tags"] = ", ".join(updated)
        return f"Tags {*tags} added for Snippet ID: {snippet_id}"

    def _remove_tag(self, snippet_id, tag, tags):
        if len(tags) == 0:
            raise NoTagsPresent(snippet_id)
        if tag not in tags:
            raise TagNotFound(snippet_id, tag)
        tags = tags.split(", ")
        tags.remove(tag)
        self.repository[snippet_id]["tags"] = ", ".join(tags)
        return f"{tag} removed from Tags for Snippet ID: {snippet_id}"


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

    def tag(self, snippet_id, tag, remove=False):
        pass

    def _add_tag(self, snippet_id, tag, tags):
        pass

    def _remove_tag(self, snippet_id, tag, tags):
        pass


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
