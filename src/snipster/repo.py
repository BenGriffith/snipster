from abc import ABC, abstractmethod

from sqlmodel import select

from src.snipster.exceptions import SnippetExists, SnippetNotFound
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
