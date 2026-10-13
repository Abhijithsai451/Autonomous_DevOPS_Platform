from sqlalchemy import Column, String, Text, JSON
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class AgentLongTermMemoryModel(Base):
    __tablename__ = "agent_long_term_memory"

    id = Column(String, primary_key = True)
    agent_id = Column(String, index=True, nullable=False)
    key = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default={})
    embedding = Column(Vector(1536), nullable=True) # for small models like OpenAI text-embedding-3-small with 1536 dimentions
