import hashlib
import re
import uuid
from pathlib import Path
from typing import Any, List, Dict
from openai import AsyncOpenAI
from sqlalchemy import text, desc
from sqlalchemy.orm import Session
from apps.agent_runtime.domain.rag_domain import KBDocuments, KBChunks


class KBRepository:
    def __init__(self, db: Session, embedding_client: Any = None):
        self.db = db
        if embedding_client is not None:
            self.embedding_client = embedding_client
        else:
            try:
                from openai import AsyncOpenAI
                self.embedding_client = AsyncOpenAI()
            except ImportError:
                self.embedding_client = None

    async def get_embedding(self, text_content: str) -> List[float]:
        """Generate embedding vector using the configured client."""
        if self.embedding_client is None:
            raise RuntimeError( "Embedding Client is not configured. Install 'openai' ")

        if hasattr(self.embedding_client, "embeddings") and hasattr(self.embedding_client.embeddings, "create"):
            response = await self.embedding_client.embeddings.create(
                model="text-embedding-3-small",
                input=text_content,
            )
            return response.data[0].embedding
        elif hasattr(self.embedding_client, "create"):
            res = await self.embedding_client.create(
                model="text-embedding-3-small",
                input=text_content,
            )
            return res.data[0].embedding
        elif hasattr(self.embedding_client, "aembed_query"):
            return await self.embedding_client.aembed_query(text_content)

        raise NotImplementedError(
            "Embedding client must support 'embeddings.create', 'create', or 'aembed_query'."
        )

    @staticmethod
    def _split_into_chunks(content: str, max_chunk_chars: int = 1500) -> List[str]:
        """Splits markdown/text content into paragraph-aware chunks."""
        paragraphs = content.split("\n\n")
        chunks: List[str] = []
        current_chunk = ""

        for paragraph in paragraphs:
            para = paragraph.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) <= max_chunk_chars:
                current_chunk = f"{current_chunk}\n\n{para}".strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = para

        if current_chunk:
            chunks.append(current_chunk)

        return chunks if chunks else [content.strip()]

    @staticmethod
    def update_version(version_str: str) -> str:
        """Increments patch version: e.g., '1.0.0' -> '1.0.1'."""
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version_str)
        if match:
            major, minor, patch = match.groups()
            return f"{major}.{minor}.{int(patch) + 1}"
        return f"{version_str}.1"

    async def ingest_kb(self, path: str)-> List[KBDocuments]:
        """
        Scans the provided folder path for the files - detects modified/new files.
        """
        """
                Single entry point for KB ingestion.
                Accepts the directory path string, scans files, manages versioning via SHA-256,
                computes vector embeddings, and stores them in PostgreSQL.
                """
        directory = Path(path)
        if not directory.exists() or not directory.is_dir():
            raise ValueError(f"Specified path '{path}' does not exist or is not a directory.")

        files = sorted(
            [
                f for f in directory.rglob("*")
                if f.is_file() and not f.name.startswith(".") and f.suffix in {".md", ".txt"}
            ]
        )

        persisted_documents: List[KBDocuments] = []

        for file_path in files:
            content = file_path.read_text(encoding="utf-8").strip()
            if not content:
                continue

            stem = file_path.stem
            kb_id = stem.split("-")[0] if "-" in stem else stem
            title = stem.replace("_", " ").replace("-", " ").title()

            content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()

            latest_doc = (
                self.db.query(KBDocuments)
                .filter(KBDocuments.kb_id == kb_id)
                .order_by(desc(KBDocuments.created_at))
                .first()
            )

            if latest_doc and latest_doc.content_sha256 == content_sha256:
                continue

            if latest_doc and latest_doc.version:
                next_version = self.update_version(latest_doc.version)
            else:
                next_version = "1.0.0"

            doc = KBDocuments(
                id=uuid.uuid4(),
                kb_id=kb_id,
                title=title,
                version=next_version,
                domain="specifications",
                content_sha256=content_sha256,
            )
            self.db.add(doc)
            self.db.flush()

            chunks = self._split_into_chunks(content)
            for chunk_text in chunks:
                vector_embedding = await self.get_embedding(chunk_text)

                chunk = KBChunks(
                    id=uuid.uuid4(),
                    document_id=doc.id,
                    content=chunk_text,
                    embedding=vector_embedding,
                )
                self.db.add(chunk)

            self.db.commit()
            self.db.refresh(doc)
            persisted_documents.append(doc)

        return persisted_documents


    async def search_hybrid(self,query: str,version: str = "1.0.0",limit: int = 5,
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