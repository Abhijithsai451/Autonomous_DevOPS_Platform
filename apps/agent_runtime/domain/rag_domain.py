import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship
from apps.agent_runtime.infrastructure.base import Base
from sqlalchemy import Column, UUID, String, text, func, DateTime, Text, ForeignKey


class KBDocuments(Base):
    __tablename__ = "kb_documents"
    __table_args__ = {"schema":"agent_runtime"}

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,server_default=text("gen_random_uuid()"),)
    kb_id = Column(String(32), nullable=False)
    title = Column(Text, nullable=False)
    version = Column(String(16), default="1.0.0", server_default="1.0.0")
    domain = Column(String(64), nullable=False)
    content_sha256 = Column(String(64), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True),default=datetime.utcnow,server_default=func.current_timestamp())

    chunks = relationship("KBChunks", back_populates="document", cascade="all, delete-orphan")


class KBChunks(Base):
    __tablename__ = "kb_chunks"
    __table_args__ = {"schema": "agent_runtime"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, )
    document_id = Column(UUID(as_uuid=True), ForeignKey("agent_runtime.kb_documents.id", ondelete="CASCADE"),
                         nullable=False, )
    content = Column(Text, nullable=False)
    content_tsv = Column(TSVECTOR, server_default=text("to_tsvector('english', content)"), )
    embedding = Column(Vector(1536), nullable=True, )
    document = relationship("KBDocuments", back_populates="chunks")


