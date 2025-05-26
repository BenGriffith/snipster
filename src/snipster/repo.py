from abc import ABC, abstractmethod

from src.snipster.exceptions import SnippetExists, SnippetNotFound


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
        raise SnippetNotFound(snippet_id)

    def delete(self, snippet_id):
        if snippet_id in self.repository:
            del self.repository[snippet_id]
            return f"Snippet ID: {snippet_id} was deleted and removed from the Snippet Repository"
        raise SnippetNotFound(snippet_id)


class DatastoreRepository(SnippetRepository):
    def __init__(self):
        pass

    def add(self, snippet):
        pass

    def all(self):
        pass

    def get(self, snippet):
        pass

    def delete(self, snippet):
        pass
