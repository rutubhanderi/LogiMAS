from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from ..database import Base


class Customer(Base):
    """Customer/User model for authentication and user management"""
    __tablename__ = "customers"
    __table_args__ = {"schema": "public"}
    
    customer_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    phone = Column(String)
    address = Column(JSONB)
    role = Column(String, nullable=False, default="customer")
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    hashed_password = Column(String, nullable=False)
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Relationship to orders
    orders = relationship("Order", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(email={self.email}, role={self.role})>"
