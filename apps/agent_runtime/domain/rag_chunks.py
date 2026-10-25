import uuid
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from apps.agent_runtime.domain.rag_domain import KBDocuments
from apps.agent_runtime.infrastructure.base import Base
from sqlalchemy.dialects.postgresql import  TSVECTOR
from sqlalchemy import Column, UUID,  text,  ForeignKey, Text

class KBChunks(Base):
    __tablename__ = "kb_chunks"
    __table_args__ = {"schema": "agent_runtime"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, )
    document_id = Column(UUID(as_uuid=True), ForeignKey("agent_runtime.kb_documents.id", ondelete="CASCADE"),
                         nullable=False, )
    content = Column(Text, nullable=False)
    content_tsv = Column(TSVECTOR, server_default=text("to_tsvector('english', content)"), )
    embedding = Column(Vector(1536), nullable=True, )
    document = relationship(KBDocuments, back_populates="chunks")
