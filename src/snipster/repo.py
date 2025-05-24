from abc import ABC, abstractmethod


class SnippetRepository(ABC):
    @abstractmethod
    def add(self):
        pass

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def delete(self):
        pass
