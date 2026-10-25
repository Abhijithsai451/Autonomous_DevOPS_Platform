import hashlib
import uuid
from typing import Any, List, Dict

from sqlalchemy import text
from sqlalchemy.orm import Session

from apps.agent_runtime.domain.rag_domain import KBDocuments, KBChunks


class KBRepository:
    def __init__(self, db: Session, embedding_client: Any = None):
        self.db = db
        self.embedding_client = embedding_client

    async def get_embedding(self, text_content: str) -> List[float]:
        """Generate embedding vector using the configured client."""
        if hasattr(self.embedding_client, "aembed_query"):
            return await self.embedding_client.aembed_query(text_content)
        elif hasattr(self.embedding_client, "create"):
            res = await self.embedding_client.create(input=text_content)
            return res.data[0].embedding
        raise NotImplementedError("An embedding client with 'aembed_query' or 'create' is required.")

    async def ingest_document(
        self,
        kb_id: str,
        title: str,
        domain: str,
        content: str,
        chunks: List[str],
        version: str = "1.0.0",
    ) -> KBDocuments:
        """Ingest a KB document and its associated vector chunks."""
        content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()

        # 1. Create document record
        doc = KBDocuments(
            id=uuid.uuid4(),
            kb_id=kb_id,
            title=title,
            version=version,
            domain=domain,
            content_sha256=content_sha256,
        )
        self.db.add(doc)
        self.db.flush()

        # 2. Embed and insert chunks
        for chunk_text in chunks:
            embedding = await self.get_embedding(chunk_text) if self.embedding_client else None
            chunk = KBChunks(
                id=uuid.uuid4(),
                document_id=doc.id,
                content=chunk_text,
                embedding=embedding,
            )
            self.db.add(chunk)

        self.db.commit()
        self.db.refresh(doc)
        return doc

    async def search_hybrid(
        self,
        query: str,
        version: str = "1.0.0",
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search (FTS + pgvector with RRF) via PostgreSQL stored function."""
        query_vector = await self.get_embedding(query)

        sql = text("""
            SELECT chunk_id, kb_id, content, combined_score
            FROM agent_runtime.search_kb_hybrid(
                :query_embedding::vector,
                :query_text,
                :match_version,
                :match_limit
            );
        """)

        result = self.db.execute(
            sql,
            {
                "query_embedding": str(query_vector),
                "query_text": query,
                "match_version": version,
                "match_limit": limit,
            },
        )

        rows = result.fetchall()
        return [
            {
                "chunk_id": row.chunk_id,
                "kb_id": row.kb_id,
                "content": row.content,
                "score": float(row.combined_score),
            }
            for row in rows
        ]

    async def retrieve_context(self, query: str, limit: int = 3) -> str:
        """Retrieve formatted specification context for prompt injection."""
        hits = await self.search_hybrid(query=query, limit=limit)
        if not hits:
            return "No relevant specification context found."

        parts = [
            f"[{hit['kb_id']}] (Relevance Score: {hit['score']:.4f})\n{hit['content']}"
            for hit in hits
        ]
        return "\n\n---\n\n".join(parts)