from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List
from uuid import UUID


class BaseMemoryStore(ABC):
    @abstractmethod
    async def store(self, entity_id: UUID, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    async def retrieve(self, entity_id: UUID, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def search(self, entity_id: UUID, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID, key: str) -> None:
        pass