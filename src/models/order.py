from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from uuid import uuid4
from ..database import Base


class Order(Base):
    """Order model for customer orders"""
    __tablename__ = "orders"
    __table_args__ = {"schema": "public"}
    
    order_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id = Column(PG_UUID(as_uuid=True), ForeignKey('public.customers.customer_id'))
    order_date = Column(DateTime(timezone=True))
    order_total = Column(Numeric)
    items = Column(JSONB)
    destination = Column(JSONB)
    status = Column(String)
    estimated_delivery_date = Column(DateTime(timezone=True))
    actual_delivery_date = Column(DateTime(timezone=True))
    
    # Relationship to customer
    customer = relationship("Customer", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(order_id={self.order_id}, status={self.status})>"
