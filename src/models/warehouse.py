from sqlalchemy import Column, String, Float, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import uuid4
from ..database import Base

class Warehouse(Base):
    """Warehouse model with added capacity, utilization, and status fields"""
    __tablename__ = "warehouses"
    __table_args__ = {"schema": "public"}
    
    warehouse_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    lat = Column(Float)
    lon = Column(Float)
    region = Column(String)
    
    # --- NEW COLUMNS ---
    capacity_sq_ft = Column(Numeric)
    utilization_pct = Column(Numeric)
    # The Enum type ensures only valid statuses can be saved.
    status = Column(Enum('active', 'inactive', 'maintenance', name='warehouse_status', create_type=False), nullable=False, server_default='active')
    
    def __repr__(self):
        return f"<Warehouse(name={self.name}, region={self.region})>"