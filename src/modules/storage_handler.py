
from abc import ABC, abstractmethod

class StorageHandler(ABC):
    @abstractmethod
    def save(self, data):
        pass

    @abstractmethod
    def load(self):
        pass
