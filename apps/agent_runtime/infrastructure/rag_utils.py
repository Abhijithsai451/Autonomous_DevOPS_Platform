from typing import List, Dict, Any

from sqlalchemy.orm import Session

class RAG:
    def __init__(self, db: Session, embedding_client: None):
        self.vector_repo = None
        self.embedding_client = embedding_client

    async def generate_embeddings(self, text_content: str) -> List[float]:
        raise NotImplementedError("connect your preferred LLM embedding provider")

    async def ingest_document(self, source_id:str, content: str, metadata: Dict[str, Any]=None)-> None:
        embedding = await self.generate_embedding(content)
        self.vector_repo.insert_embedding(source_id=source_id, content=content, embedding=embedding, metadata=metadata)
        self.db.commit()

    async def retrieve_context(self, query: str, limit: int = 3) -> str:
        query_embedding = await self.generate_embedding(query)
        matches = self.vector_repo.similarity_search(query_embedding=query_embedding, limit=limit)

        if not matches:
            return "No relevant context found."

        context_block = "\n\n".join([f"Source ({m['source_id']}):\n{m['content']}" for m in matches])
        return context_block


