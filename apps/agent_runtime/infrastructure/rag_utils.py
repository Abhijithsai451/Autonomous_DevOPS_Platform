import math
from typing import Any, Dict, List, Optional
from uuid import uuid4
from sqlalchemy.orm import Session

from apps.agent_runtime.domain.rag_storage import RAGStorage

class RAG:
    def __init__(self, db: Session, embedding_client: Any = None):
        self.db = db
        self.embedding_client = embedding_client

    async def generate_embeddings(self, text_content: str) -> List[float]:
        if self.embedding_client is not None and hasattr(self.embedding_client, "embed_query"):
            return await self.embedding_client.aembed_query(text_content)
        elif self.embedding_client is not None and hasattr(self.embedding_client, "create"):
            res = await self.embedding_client.create(input=text_content)
            return res.data[0].embedding
        raise NotImplementedError("Connect your preferred LLM embedding provider or pass embedding_client.")

    async def ingest_document(self,filename: str,file_path: str,content: str,vector: Optional[List[float]] = None,
                                                        ) -> RAGStorage:
        if vector is None:
            vector = await self.generate_embeddings(content)
        record = RAGStorage(
            id=uuid4(),
            filename=filename,
            file_path=file_path,
            vector=vector,
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    async def retrieve_context(self, query: str, limit: int = 3) -> str:
        query_vector = await self.generate_embeddings(query)

        records: List[RAGStorage] = self.db.query(RAGStorage).all()
        if not records:
            return "No relevant specification context found."

        scored_records = []
        for doc in records:
            if doc.vector:
                similarity = self._cosine_similarity(query_vector, doc.vector)
                scored_records.append((similarity, doc))

        scored_records.sort(key=lambda item: item[0], reverse=True)
        top_matches = scored_records[:limit]

        if not top_matches:
            return "No relevant context found."

        context_parts = []
        for score, doc in top_matches:
            context_parts.append(
                f"Specification Doc: {doc.filename} (Score: {score:.3f})\n"
                f"Path: {doc.file_path}"
            )

        return "\n\n".join(context_parts)

