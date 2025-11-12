from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from ..database import Base


class Inventory(Base):
    """Inventory model for warehouse stock management"""
    __tablename__ = "inventory"
    __table_args__ = {"schema": "public"}
    
    inventory_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    warehouse_id = Column(PG_UUID(as_uuid=True), ForeignKey('public.warehouses.warehouse_id'))
    sku = Column(String, nullable=False)
    product_name = Column(String)
    qty_on_hand = Column(Integer, nullable=False)
    reorder_point = Column(Integer)
    
    # Relationship
    warehouse = relationship("Warehouse", backref="inventory")
    
    def __repr__(self):
        return f"<Inventory(sku={self.sku}, qty={self.qty_on_hand})>"
