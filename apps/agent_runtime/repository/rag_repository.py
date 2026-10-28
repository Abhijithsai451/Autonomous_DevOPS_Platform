import hashlib
import re
import uuid
from pathlib import Path
from typing import Any, List, Dict, Optional
from openai import AsyncOpenAI
from sqlalchemy import text, desc, bindparam, type_coerce
from sqlalchemy.orm import Session
from apps.agent_runtime.domain.rag_domain import KBDocuments, KBChunks
from apps.agent_runtime.config.settings import agent_runtime_settings as settings
from apps.agent_runtime.infrastructure.database import agent_db_session



class KBRepository:
    def __init__(self, db: Session, embedding_client: Any = None):
        self.db = db
        if embedding_client is not None:
            self.embedding_client = embedding_client
        else:
            try:
                self.embedding_client = AsyncOpenAI(
                    base_url=settings.OLLAMA_BASE_URL,
                    api_key=settings.OPENAI_API_KEY,
                )
            except ImportError:
                self.embedding_client = None


    async def get_embedding(self, text_content: str) -> List[float]:
        """Generate embedding vector using the configured client."""
        response = await self.embedding_client.embeddings.create(
            model = settings.EMBEDDING_MODEL,
            input = text_content
        )
        return response.data[0].embedding

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
            relative_path = file_path.relative_to(directory)
            if len(relative_path.parts)>1:
                domain = relative_path.parts[0]
            else:
                domain = "general"
            stem = file_path.stem
            kb_id = stem.split("-")[0] if "-" in stem else stem
            title = stem.replace("_", " ").replace("-", " ").title()

            content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
            existing_doc = (self.db.query(KBDocuments).filter(KBDocuments.content_sha256 == content_sha256).first())
            if existing_doc:
                continue
            latest_doc = (self.db.query(KBDocuments).filter(KBDocuments.kb_id == kb_id).order_by(desc(KBDocuments.created_at)).first())

            if latest_doc and latest_doc.version:
                next_version = self.update_version(latest_doc.version)
            else:
                next_version = "1.0.0"

            doc = KBDocuments(id=uuid.uuid4(),kb_id=kb_id,title=title,version=next_version,domain=domain,
                                content_sha256=content_sha256,)
            self.db.add(doc)
            self.db.flush()

            chunks = self._split_into_chunks(content)
            for chunk_text in chunks:
                vector_embedding = await self.get_embedding(chunk_text)

                chunk = KBChunks(id=uuid.uuid4(),document_id=doc.id,content=chunk_text,embedding=vector_embedding)
                self.db.add(chunk)

            self.db.commit()
            self.db.refresh(doc)
            persisted_documents.append(doc)

        return persisted_documents


    async def search_hybrid(self,query: str,version: str = "1.0.0",limit: int = 5,
                            domain: Optional[str]=None) -> List[Dict[str, Any]]:
        """Perform hybrid search (FTS + pgvector with RRF) via PostgreSQL stored function."""
        query_vector = await self.get_embedding(query)
        distance = KBChunks.embedding.cosine_distance(query_vector)
        stmt = (
            self.db.query(
                KBChunks.id.label("chunk_id"),
                KBDocuments.kb_id.label("kb_id"),
                KBChunks.content.label("content"),
                (1.0 - distance).label("score"),
            )
            .join(KBDocuments, KBChunks.document_id == KBDocuments.id)
            .filter(KBDocuments.version == version)
        )

        if domain:
            stmt = stmt.filter(KBDocuments.domain == domain)

        rows = stmt.order_by(distance).limit(limit).all()

        return [
            {
                "chunk_id": row.chunk_id,
                "kb_id": row.kb_id,
                "content": row.content,
                "score": float(row.score) if row.score is not None else 0.0,
            }
            for row in rows
        ]


    async def retrieve_context(self, query: str, limit: int = 3,domain: Optional[str] = None) -> str:
        """Retrieve formatted specification context for prompt injection."""
        hits = await self.search_hybrid(query=query, limit=limit,domain = domain)
        if not hits:
            return "No relevant specification context found."

        parts = [
            f"[{hit['kb_id']}] (Relevance Score: {hit['score']:.4f})\n{hit['content']}"
            for hit in hits
        ]
        return "\n\n---\n\n".join(parts)


rag_repo = KBRepository(agent_db_session)