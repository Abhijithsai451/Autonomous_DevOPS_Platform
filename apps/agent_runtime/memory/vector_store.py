from typing import List, Dict, Any, Optional
from uuid import UUID

from sqlalchemy import select
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger

from apps.agent_runtime.memory.base import BaseMemoryStore
from apps.agent_runtime.memory.vector_memory_model import AgentLongTermMemoryModel


class PostgresVectorMemory(BaseMemoryStore):
    def __init__(self, db_session_factory, embedding_client):
        """
        :param db_session_factory: SQLAlchemy session factory
        :param embedding_client: Client to generate vector embeddings (e.g., OpenAIEmbeddings)
        """
        self.session_factory = db_session_factory
        self.embedding_client = embedding_client

    async def store(
            self,
            entity_id: UUID,
            key: str,
            value: Any,
            metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Stores text or structured memory along with its generated vector embedding.
        """
        text_content = str(value)
        # Generate embedding vector
        embedding = await self.embedding_client.aembed_query(text_content)

        with self.session_factory() as session:
            memory_id = f"{entity_id}:{key}"
            existing = session.get(AgentLongTermMemoryModel, memory_id)

            if existing:
                existing.content = text_content
                existing.metadata_json = metadata or {}
                existing.embedding = embedding
            else:
                new_memory = AgentLongTermMemoryModel(
                    id=memory_id,
                    agent_id=str(entity_id),
                    key=key,
                    content=text_content,
                    metadata_json=metadata or {},
                    embedding=embedding
                )
                session.add(new_memory)

            session.commit()
            logger.info(f"Stored long-term memory for agent {entity_id} under key '{key}'")

    async def retrieve(self, entity_id: UUID, key: str) -> Optional[Any]:
        with self.session_factory() as session:
            memory_id = f"{entity_id}:{key}"
            record = session.get(AgentLongTermMemoryModel, memory_id)
            return record.content if record else None

    async def search(self, entity_id: UUID, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Performs vector similarity search using pgvector's cosine distance operator (<=>).
        """
        query_embedding = await self.embedding_client.aembed_query(query)

        with self.session_factory() as session:
            # pgvector cosine distance search
            stmt = (
                select(AgentLongTermMemoryModel)
                .filter(AgentLongTermMemoryModel.agent_id == str(entity_id))
                .order_by(AgentLongTermMemoryModel.embedding.cosine_distance(query_embedding))
                .limit(limit)
            )
            results = session.scalars(stmt).all()

            return [
                {
                    "key": r.key,
                    "content": r.content,
                    "metadata": r.metadata_json
                }
                for r in results
            ]

    async def delete(self, entity_id: UUID, key: str) -> None:
        with self.session_factory() as session:
            memory_id = f"{entity_id}:{key}"
            record = session.get(AgentLongTermMemoryModel, memory_id)
            if record:
                session.delete(record)
                session.commit()
                logger.info(f"Deleted memory '{key}' for agent {entity_id}")

