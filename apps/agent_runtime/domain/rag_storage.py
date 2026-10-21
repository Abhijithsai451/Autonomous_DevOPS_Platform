from uuid import uuid4
from apps.agent_runtime.infrastructure.base import Base
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Column, UUID, String, Float


class RAGStorage(Base):
    __tablename__ = "rag_storage"
    __table_args__ = {"schema":"agent_runtime"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    filename= Column(String(255), nullable = False)
    file_path= Column(String(255), nullable = False)
    vector = Column(ARRAY(Float), nullable = False)

