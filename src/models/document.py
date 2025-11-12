from sqlalchemy import Column, String, Integer, DateTime, Text, LargeBinary
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import uuid4
from ..database import Base

# Try to import pgvector, but make it optional
try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    # Fallback to LargeBinary if pgvector is not installed
    Vector = None


class Document(Base):
    """Document model for vector embeddings and similarity search"""
    __tablename__ = "documents"
    __table_args__ = {"schema": "public"}
    
    doc_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_type = Column(String)
    source_id = Column(String)
    region_id = Column(String)
    ts = Column(DateTime(timezone=True))
    chunk_index = Column(Integer)
    text_snippet = Column(Text)
    embedding_model = Column(String)
    
    # Use Vector if pgvector is available, otherwise use LargeBinary
    if PGVECTOR_AVAILABLE:
        embedding = Column(Vector(384))
    else:
        # Store as binary data if pgvector is not installed
        embedding = Column(LargeBinary)
    
    def __repr__(self):
        return f"<Document(doc_id={self.doc_id}, source_type={self.source_type})>"
